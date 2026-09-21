package com.car.analysis.recommendation.recall

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

object ContentBased {

  def run(spark: SparkSession): DataFrame = {
    import spark.implicits._
    val props = getProps()

    val behaviorDF = spark.read.jdbc(AppConfig.MySQL.url, "user_behavior", props)
      .filter($"car_id" > 0)
    val carInfoDF = spark.read.jdbc(AppConfig.MySQL.url, "car_info", props)

    // Cars already interacted with
    val interacted = behaviorDF
      .select("user_id", "car_id")
      .distinct()

    // Compute user preferences from behavior history
    val userCarPrefs = behaviorDF
      .join(carInfoDF, Seq("car_id"), "left")
      .filter($"brand_name".isNotNull)
      .groupBy("user_id")
      .agg(
        collect_set("brand_name").as("preferred_brands"),
        collect_set("car_type").as("preferred_types"),
        collect_set("fuel_type").as("preferred_fuels"),
        avg("price").as("avg_price"),
        min("price").as("min_price"),
        max("price").as("max_price")
      )

    // Cross join with on-sale cars, exclude already-interacted ones
    val contentRecs = userCarPrefs
      .crossJoin(carInfoDF.filter($"is_on_sale" === 1))
      .join(interacted, Seq("user_id", "car_id"), "left_anti")
      .withColumn("brand_match",
        when(array_contains($"preferred_brands", $"brand_name"), lit(5.0)).otherwise(lit(0.0)))
      .withColumn("type_match",
        when(array_contains($"preferred_types", $"car_type"), lit(3.0)).otherwise(lit(0.0)))
      .withColumn("fuel_match",
        when(array_contains($"preferred_fuels", $"fuel_type"), lit(2.0)).otherwise(lit(0.0)))
      .withColumn("price_range_match",
        when($"min_price".isNotNull && $"max_price".isNotNull &&
          $"price".between($"min_price" * 0.7, $"max_price" * 1.3), lit(1.0)).otherwise(lit(0.0)))
      .withColumn("score",
        $"brand_match" + $"type_match" + $"fuel_match" + $"price_range_match")
      .filter($"score" > 0)
      .select($"user_id", $"car_id", $"score",
        lit("content_based").as("rec_type"),
        concat_ws(" + ",
          when($"brand_match" > 0, concat(lit("偏好品牌:"), $"brand_name")),
          when($"type_match" > 0, lit("类型匹配")),
          when($"fuel_match" > 0, lit("燃料匹配")),
          when($"price_range_match" > 0, lit("价格相近"))
        ).as("reason"))

    println(s"[CB] Generated ${contentRecs.count()} recs")
    contentRecs
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}