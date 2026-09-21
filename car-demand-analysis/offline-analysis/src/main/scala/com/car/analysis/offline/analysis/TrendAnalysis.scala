package com.car.analysis.offline.analysis

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{SaveMode, SparkSession}
import org.apache.spark.sql.functions._

object TrendAnalysis {

  def run(spark: SparkSession): Unit = {
    import spark.implicits._
    val props = getProps()

    val realtimeStatsDF = spark.read.jdbc(AppConfig.MySQL.url, "realtime_stats", props)

    val dailyAgg = realtimeStatsDF
      .filter($"target_name".isNotNull
        && $"target_name" =!= "global_search"
        && !$"target_name".cast("int").isNotNull)
      .groupBy("stats_type", "target_id", "target_name", "stats_date")
      .agg(
        sum("pv").as("pv"),
        sum("uv").as("uv"),
        sum("search_count").as("search_count"),
        sum("consult_count").as("consult_count"),
        sum("collect_count").as("collect_count"),
        sum("compare_count").as("compare_count"),
        lit(0).as("order_count"),
        lit(0.0).as("conversion_rate")
      )
      .select("stats_type", "target_id", "target_name",
        "pv", "uv", "search_count", "consult_count", "collect_count",
        "compare_count", "order_count", "conversion_rate", "stats_date")

    dailyAgg.write.mode("overwrite").jdbc(AppConfig.MySQL.url, "daily_stats", props)

    println(s"[TrendAnalysis] ${dailyAgg.count()} rows -> daily_stats")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
