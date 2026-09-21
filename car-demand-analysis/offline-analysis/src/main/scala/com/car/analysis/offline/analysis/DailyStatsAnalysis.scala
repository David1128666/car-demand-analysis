package com.car.analysis.offline.analysis

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{SparkSession}
import org.apache.spark.sql.functions._

object DailyStatsAnalysis {

  def run(spark: SparkSession): Unit = {
    import spark.implicits._
    val props = new java.util.Properties()
    props.setProperty("user", AppConfig.MySQL.user)
    props.setProperty("password", AppConfig.MySQL.password)
    props.setProperty("driver", AppConfig.MySQL.driver)

    val realtimeStatsDF = spark.read.jdbc(AppConfig.MySQL.url, "realtime_stats", props)

    val summary = realtimeStatsDF
      .groupBy("stats_date")
      .agg(
        sum("pv").as("total_pv"),
        sum("uv").as("total_uv"),
        sum("search_count").as("total_search"),
        sum("consult_count").as("total_consult"),
        sum("collect_count").as("total_collect")
      )
      .orderBy($"stats_date".desc)
      .limit(30)

    summary.show(30, truncate = false)

    val topBrands = realtimeStatsDF
      .filter($"stats_type".startsWith("beh_"))
      .groupBy("target_name")
      .agg(sum("pv").as("total_pv"))
      .orderBy($"total_pv".desc)
      .limit(10)

    topBrands.show(10, truncate = false)

    println(s"[DailyStatsAnalysis] Done")
  }
}
