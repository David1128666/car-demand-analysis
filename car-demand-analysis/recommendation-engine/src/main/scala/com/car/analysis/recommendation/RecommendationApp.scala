package com.car.analysis.recommendation

import com.car.analysis.common.config.AppConfig
import com.car.analysis.recommendation.recall.{CollaborativeFiltering, ContentBased, HotRecommendation}
import com.car.analysis.recommendation.rank.RankingStrategy
import org.apache.spark.sql.{SaveMode, SparkSession}
import java.sql.DriverManager

object RecommendationApp {

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName(s"${AppConfig.Spark.appName}-Recommendation")
      .master(AppConfig.Spark.master)
      .config("spark.sql.adaptive.enabled", "false")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    try {
      println(">>> Recommendation Engine started.")

      println("[1/4] Collaborative Filtering...")
      val cfDF = CollaborativeFiltering.run(spark)

      println("[2/4] Content-Based...")
      val cbDF = ContentBased.run(spark)

      println("[3/4] Hot recommendation...")
      val hotDF = HotRecommendation.run(spark)

      println("[4/4] Merging + ranking...")
      val finalRecsDF = RankingStrategy.rank(cfDF, cbDF, hotDF, spark)

      val props = new java.util.Properties()
      props.setProperty("user", AppConfig.MySQL.user)
      props.setProperty("password", AppConfig.MySQL.password)
      props.setProperty("driver", AppConfig.MySQL.driver)

      // Write to staging table first, then atomically swap (avoid empty table on failure)
      finalRecsDF.write
        .mode(SaveMode.Overwrite)
        .option("truncate", "true")
        .jdbc(AppConfig.MySQL.url, "recommendation_staging", props)

      replaceTable("recommendation_staging", "recommendation")

      val count = finalRecsDF.count()
      println(s">>> Done. $count recommendations saved to recommendation table.")
    } finally {
      spark.stop()
    }
  }

  private def replaceTable(staging: String, target: String): Unit = {
    val conn = DriverManager.getConnection(AppConfig.MySQL.url, AppConfig.MySQL.user, AppConfig.MySQL.password)
    try {
      val stmt = conn.createStatement()
      stmt.executeUpdate(s"DROP TABLE IF EXISTS ${target}_swap")
      stmt.executeUpdate(s"RENAME TABLE $target TO ${target}_swap, $staging TO $target")
      stmt.executeUpdate(s"DROP TABLE IF EXISTS ${target}_swap")
      println(s"[REC] Atomic replace: $staging -> $target")
    } finally {
      conn.close()
    }
  }
}