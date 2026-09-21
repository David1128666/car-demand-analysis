package com.car.analysis.recommendation.recall

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

object HotRecommendation {

  def run(spark: SparkSession): DataFrame = {
    import spark.implicits._
    val props = getProps()

    val behaviorDF = spark.read.jdbc(AppConfig.MySQL.url, "user_behavior", props)
      .filter($"car_id" > 0)
    val carInfoDF = spark.read.jdbc(AppConfig.MySQL.url, "car_info", props)

    val hotCars = behaviorDF
      .join(carInfoDF, Seq("car_id"), "left")
      .filter($"is_on_sale" === 1)
      .groupBy("car_id")
      .agg(
        count("*").as("view_count"),
        countDistinct("user_id").as("unique_users"),
        sum(when($"behavior_type" === "collect", 1).otherwise(0)).as("collect_count"),
        sum(when($"behavior_type" === "consult", 1).otherwise(0)).as("consult_count")
      )
      .orderBy($"view_count".desc)
      .limit(50)
      .withColumn("raw_score",
        $"view_count" * 0.4 + $"unique_users" * 0.3 +
          $"collect_count" * 0.2 + $"consult_count" * 0.1)

    // Min-max normalize to [0.1, 10.0] to fit MySQL DECIMAL column
    val scoreStats = hotCars.agg(max("raw_score"), min("raw_score")).head()
    val hotMax = scoreStats.getDouble(0)
    val hotMin = scoreStats.getDouble(1)
    val range = if (hotMax > hotMin) hotMax - hotMin else 1.0

    val normalizedHot = hotCars
      .withColumn("score",
        round((($"raw_score" - lit(hotMin)) / lit(range)) * lit(9.98) + lit(0.01), 4))
      .select("car_id", "score")

    val users = behaviorDF.select("user_id").distinct()

    val hotRecs = users.crossJoin(normalizedHot)
      .select($"user_id", $"car_id", $"score",
        lit("hot").as("rec_type"),
        lit("trending hot model").as("reason"))

    println(s"[HOT] Generated ${hotRecs.count()} recs")
    hotRecs
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
