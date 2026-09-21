package com.car.analysis.realtime.processor

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._

object ConsultStatsProcessor {

  def process(df: DataFrame, spark: SparkSession, batchId: Long): Unit = {
    import spark.implicits._
    val props = getProps()

    val statsDF = df
      .filter($"car_id".isNotNull && $"consult_type".isNotNull)
      .groupBy(
        $"car_id",
        $"consult_type",
        date_format(current_timestamp(), "yyyy-MM-dd").as("stats_date"),
        hour(current_timestamp()).as("stats_hour"),
        concat(lpad(minute(current_timestamp()), 2, "0"), lit(":"), lpad(floor(second(current_timestamp()) / 5) * 5, 2, "0")).as("stats_minute"))
      .agg(
        count("*").as("pv"),
        countDistinct("user_id").as("uv"),
        count("*").as("consult_count")
      )
      .select(
        lit("consult").as("stats_type"),
        $"car_id".as("target_id"),
        lit("????").as("target_name"),
        $"pv", $"uv",
        lit(0).as("search_count"),
        $"consult_count",
        lit(0).as("collect_count"),
        lit(0).as("compare_count"),
        $"stats_date", $"stats_hour", $"stats_minute"
      )
      .dropDuplicates("stats_type", "target_id", "stats_date", "stats_hour", "stats_minute")

    statsDF.write.mode("append").jdbc(AppConfig.MySQL.url, "realtime_stats", props)

    val logDF = df
      .filter($"followup_status".isNotNull)
      .groupBy($"followup_status")
      .agg(count("*").as("cnt"))
      .select(
        lit("system").as("operator_id"),
        lit("realtime").as("operator_name"),
        lit("consult_followup").as("operation_type"),
        lit("consult").as("operation_module"),
        concat($"followup_status", lit(": "), $"cnt").as("operation_desc"),
        lit("POST").as("request_method"),
        lit("/api/realtime/consult").as("request_url"),
        lit("200").as("response_code"),
        lit("success").as("response_msg"),
        lit(1).as("status")
      )

    logDF.write.mode("append").jdbc(AppConfig.MySQL.url, "operation_log", props)
    println(s"[Batch $batchId] car-consult: processed")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}