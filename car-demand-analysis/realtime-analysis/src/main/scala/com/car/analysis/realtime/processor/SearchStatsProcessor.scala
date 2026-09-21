package com.car.analysis.realtime.processor

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

object SearchStatsProcessor {

  def process(df: DataFrame, spark: SparkSession, batchId: Long): Unit = {
    import spark.implicits._
    val props = getProps()

    val statsDF = df
      .groupBy(
        date_format(current_timestamp(), "yyyy-MM-dd").as("stats_date"),
        hour(current_timestamp()).as("stats_hour"),
        concat(lpad(minute(current_timestamp()), 2, "0"), lit(":"), lpad(floor(second(current_timestamp()) / 5) * 5, 2, "0")).as("stats_minute"))
      .agg(
        count("*").as("pv"),
        countDistinct("user_id").as("uv"),
        count("*").as("search_count")
      )
      .select(
        lit("search").as("stats_type"),
        lit(1).as("target_id"),
        lit("????").as("target_name"),
        $"pv", $"uv",
        $"search_count",
        lit(0).as("consult_count"),
        lit(0).as("collect_count"),
        lit(0).as("compare_count"),
        $"stats_date", $"stats_hour", $"stats_minute"
      )
      .dropDuplicates("stats_type", "target_id", "stats_date", "stats_hour", "stats_minute")

    statsDF.write.mode("append").jdbc(AppConfig.MySQL.url, "realtime_stats", props)

    val searchLogDF = df
      .filter($"search_keyword".isNotNull)
      .select(
        $"user_id",
        lit("").as("session_id"),
        $"search_keyword".as("keyword"),
        lit("general").as("search_type"),
        (unix_timestamp(current_timestamp()) * 1000).cast("bigint").as("timestamp")
      )

    searchLogDF.write.mode("append").jdbc(AppConfig.MySQL.url, "search_log", props)
    println(s"[Batch $batchId] car-search: processed")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}