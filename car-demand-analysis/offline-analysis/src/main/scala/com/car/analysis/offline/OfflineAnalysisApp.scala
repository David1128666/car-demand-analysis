package com.car.analysis.offline

import com.car.analysis.common.config.AppConfig
import com.car.analysis.offline.analysis.{CarPreferenceAnalysis, DailyStatsAnalysis, TrendAnalysis, UserProfileAnalysis, MarketInsightAnalysis}
import org.apache.spark.sql.SparkSession

object OfflineAnalysisApp {

  def main(args: Array[String]): Unit = {
    val taskArg = if (args.length > 0) args(0) else "all"

    val spark = SparkSession.builder()
      .appName(s"${AppConfig.Spark.appName}-Offline")
      .master(AppConfig.Spark.master)
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    try {
      println(s">>> Offline Analysis started. Task: $taskArg")

      taskArg.toLowerCase match {
        case "trend"        => TrendAnalysis.run(spark)
        case "profile"      => UserProfileAnalysis.run(spark)
        case "preference"   => CarPreferenceAnalysis.run(spark)
        case "daily"        => DailyStatsAnalysis.run(spark)
        case "market"       => MarketInsightAnalysis.run(spark)
        case "all" =>
          TrendAnalysis.run(spark)
          UserProfileAnalysis.run(spark)
          CarPreferenceAnalysis.run(spark)
          DailyStatsAnalysis.run(spark)
          MarketInsightAnalysis.run(spark)
        case _ =>
          println(s"Unknown task: $taskArg. Available: trend, profile, preference, daily, market, all")
      }

      println(">>> Offline Analysis completed.")
    } finally {
      spark.stop()
    }
  }
}