package com.car.analysis.recommendation.recall

import com.car.analysis.common.config.AppConfig
import org.apache.spark.ml.recommendation.{ALS, ALSModel}
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

object CollaborativeFiltering {

  def run(spark: SparkSession): DataFrame = {
    import spark.implicits._
    val props = getProps()

    val behaviorDF = spark.read.jdbc(AppConfig.MySQL.url, "user_behavior", props)
      .filter($"car_id" > 0)

    // Only recommend cars that exist in car_info and are on sale
    val validCars = spark.read.jdbc(AppConfig.MySQL.url, "car_info", props)
      .filter($"is_on_sale" === 1)
      .select("car_id")

    // Build user_id -> user_idx mapping
    val userMapping = behaviorDF
      .select("user_id")
      .distinct()
      .withColumn("user_idx", hash($"user_id").cast("int"))

    // Build rating DataFrame with user_idx for ALS training, only valid cars
    val ratingDF = behaviorDF
      .join(validCars, Seq("car_id"), "inner")
      .join(userMapping, Seq("user_id"), "left")
      .withColumn("rating",
        when($"behavior_type" === "collect", lit(5.0))
          .when($"behavior_type" === "consult", lit(4.0))
          .when($"behavior_type" === "search", lit(3.0))
          .when($"behavior_type" === "browse", lit(2.0))
          .otherwise(lit(1.0)))
      .groupBy("user_idx", "car_id")
      .agg(avg("rating").as("rating"))

    val ratingCount = ratingDF.count()
    println(s"[CF] Training data: $ratingCount ratings")

    if (ratingCount < 100) {
      println("[CF] Insufficient data, skipping")
      return spark.emptyDataFrame
        .withColumn("user_id", lit(""))
        .withColumn("car_id", lit(0L))
        .withColumn("score", lit(0.0))
        .withColumn("rec_type", lit("collaborative"))
        .withColumn("reason", lit("similar users also viewed"))
        .limit(0)
    }

    val als = new ALS()
      .setMaxIter(10)
      .setRegParam(0.01)
      .setUserCol("user_idx")
      .setItemCol("car_id")
      .setRatingCol("rating")
      .setColdStartStrategy("drop")
      .setImplicitPrefs(false)

    val model: ALSModel = als.fit(ratingDF)

    // Map user_idx back to original user_id after ALS prediction
    val userRecs = model.recommendForAllUsers(10)
      .select($"user_idx", explode($"recommendations").as("rec"))
      .select($"user_idx", $"rec.car_id".as("car_id"), $"rec.rating".as("score"))
      .filter(!isnan($"score") && $"score" > 0.0)
      .join(validCars, Seq("car_id"), "inner")
      .join(userMapping, Seq("user_idx"), "left")
      .filter($"user_id".isNotNull)
      .withColumn("score", round($"score", 4))
      .withColumn("rec_type", lit("collaborative"))
      .withColumn("reason", lit("similar users also viewed"))
      .select("user_id", "car_id", "score", "rec_type", "reason")

    println(s"[CF] Generated ${userRecs.count()} recs")
    userRecs
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
