package com.car.analysis.recommendation.rank

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

object RankingStrategy {

  def rank(cfDF: DataFrame, cbDF: DataFrame, hotDF: DataFrame, spark: SparkSession): DataFrame = {
    import spark.implicits._

    val rankedCF = cfDF.select($"user_id", $"car_id", $"score", $"rec_type", $"reason")
    val rankedCB = cbDF.select($"user_id", $"car_id", $"score", $"rec_type", $"reason")
    val rankedHot = hotDF.select($"user_id", $"car_id", $"score", $"rec_type", $"reason")

    val mergedDF = rankedCF.unionByName(rankedCB).unionByName(rankedHot)

    if (mergedDF.isEmpty) {
      println("[RANK] No recommendations from any recall strategy, returning empty")
      return spark.emptyDataFrame
        .withColumn("user_id", lit(""))
        .withColumn("car_id", lit(0L))
        .withColumn("rec_type", lit(""))
        .withColumn("rec_position", lit(0))
        .withColumn("score", lit(0.0))
        .withColumn("reason", lit(""))
        .withColumn("reason_type", lit(""))
        .withColumn("status", lit(0))
        .select("user_id", "car_id", "rec_type", "rec_position", "score", "reason", "reason_type", "status")
        .limit(0)
    }

    val weightedDF = mergedDF
      .withColumn("weighted_score",
        when($"rec_type" === "collaborative", $"score" * 1.2)
          .when($"rec_type" === "content_based", $"score" * 1.0)
          .when($"rec_type" === "hot", $"score" * 0.8)
          .otherwise($"score"))
      .filter(!isnan($"weighted_score") && $"weighted_score".isNotNull)

    // Keep best score per (user_id, car_id) deterministically
    val scoreWindow = Window.partitionBy("user_id", "car_id").orderBy($"weighted_score".desc)
    val dedupedDF = weightedDF
      .withColumn("rn", row_number().over(scoreWindow))
      .filter($"rn" === 1)
      .drop("rn")

    // Min-max normalize to [0.01, 10.0] to fit MySQL DECIMAL column
    val bounds = dedupedDF.agg(max("weighted_score"), min("weighted_score")).head()
    val maxScore = if (bounds.isNullAt(0)) 1.0 else bounds.getDouble(0)
    val minScore = if (bounds.isNullAt(1)) 0.0 else bounds.getDouble(1)
    val scoreRange = if (maxScore > minScore) maxScore - minScore else 1.0

    val normalizedDF = dedupedDF
      .withColumn("score",
        round((($"weighted_score" - lit(minScore)) / lit(scoreRange)) * lit(9.98) + lit(0.01), 4))

    val windowSpec = Window
      .partitionBy("user_id")
      .orderBy($"score".desc)

    normalizedDF
      .withColumn("rec_position", row_number().over(windowSpec))
      .filter($"rec_position" <= 10)
      .withColumn("reason_type",
        when($"rec_type" === "collaborative", lit("similar"))
          .when($"rec_type" === "content_based", lit("brand_match"))
          .when($"rec_type" === "hot", lit("hot")))
      .withColumn("status", lit(0))
      .select("user_id", "car_id", "rec_type", "rec_position", "score", "reason", "reason_type", "status")
  }
}
