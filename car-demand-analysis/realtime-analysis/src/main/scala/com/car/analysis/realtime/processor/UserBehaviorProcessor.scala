package com.car.analysis.realtime.processor

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import java.sql.{Connection, DriverManager, PreparedStatement, Timestamp}

object UserBehaviorProcessor {

  def process(df: DataFrame, spark: SparkSession, batchId: Long): Unit = {
    import spark.implicits._
    val props = getProps()

    val result = df
      .filter($"behavior_type".isNotNull && $"brand_id".isNotNull && !$"brand_name".startsWith("??"))
      .groupBy($"behavior_type", $"brand_id", $"brand_name",
        date_format(current_timestamp(), "yyyy-MM-dd").as("stats_date"),
        hour(current_timestamp()).as("stats_hour"),
        concat(lpad(minute(current_timestamp()), 2, "0"), lit(":"), lpad(floor(second(current_timestamp()) / 5) * 5, 2, "0")).as("stats_minute"))
      .agg(
        count("*").as("pv"),
        countDistinct("user_id").as("uv"),
        sum(when($"behavior_type" === "search", 1).otherwise(0)).as("search_count"),
        sum(when($"behavior_type" === "consult", 1).otherwise(0)).as("consult_count"),
        sum(when($"behavior_type" === "collect", 1).otherwise(0)).as("collect_count"),
        sum(when($"behavior_type" === "compare", 1).otherwise(0)).as("compare_count"),
        first("car_type", true).as("car_type"),
        first("fuel_type", true).as("fuel_type")
      )
      .select(
        concat(lit("beh_"), $"behavior_type").as("stats_type"),
        $"brand_id".as("target_id"),
        $"brand_name".as("target_name"),
        $"car_type",
        $"fuel_type",
        $"pv", $"uv",
        $"search_count", $"consult_count", $"collect_count", $"compare_count",
        $"stats_date", $"stats_hour", $"stats_minute"
      )
      .dropDuplicates("stats_type", "target_id", "stats_date", "stats_hour", "stats_minute")

    result.write.mode("append").jdbc(AppConfig.MySQL.url, "realtime_stats", props)

    // Persist raw behavior to user_behavior using INSERT IGNORE to survive restarts
    val rawDF = df
      .filter($"behavior_type".isNotNull && $"user_id".isNotNull)
      .select(
        $"behavior_id", $"user_id", $"session_id",
        coalesce($"car_id", lit(0L)).as("car_id"),
        $"behavior_type",
        lit("").as("source"),
        coalesce($"search_keyword", lit("")).as("keyword"),
        lit("").as("referrer_url"),
        lit("").as("ip_address"),
        lit("").as("user_agent"),
        lit("").as("device_type"),
        (unix_timestamp(current_timestamp()) * 1000).as("timestamp"),
        current_timestamp().as("create_time")
      )
      .dropDuplicates("behavior_id")

    rawDF.foreachPartition { (iter: Iterator[Row]) =>
      var conn: Connection = null
      var stmt: PreparedStatement = null
      try {
        conn = DriverManager.getConnection(AppConfig.MySQL.url, props)
        stmt = conn.prepareStatement(
          """INSERT IGNORE INTO user_behavior
            |  (behavior_id, user_id, session_id, car_id, behavior_type,
            |   source, keyword, referrer_url, ip_address, user_agent, device_type, timestamp, create_time)
            |VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""".stripMargin)
        var count = 0
        iter.foreach { row =>
          stmt.setString(1, row.getAs[String]("behavior_id"))
          stmt.setString(2, row.getAs[String]("user_id"))
          stmt.setString(3, if (row.isNullAt(2)) "" else row.getAs[String]("session_id"))
          stmt.setLong(4, row.getAs[Long]("car_id"))
          stmt.setString(5, row.getAs[String]("behavior_type"))
          stmt.setString(6, row.getAs[String]("source"))
          stmt.setString(7, row.getAs[String]("keyword"))
          stmt.setString(8, row.getAs[String]("referrer_url"))
          stmt.setString(9, row.getAs[String]("ip_address"))
          stmt.setString(10, row.getAs[String]("user_agent"))
          stmt.setString(11, row.getAs[String]("device_type"))
          stmt.setLong(12, row.getAs[Long]("timestamp"))
          stmt.setTimestamp(13, row.getAs[Timestamp]("create_time"))
          stmt.addBatch()
          count += 1
          if (count % 500 == 0) {
            stmt.executeBatch()
          }
        }
        stmt.executeBatch()
      } finally {
        if (stmt != null) stmt.close()
        if (conn != null) conn.close()
      }
      ()
    }

    println(s"[Batch $batchId] user-behavior: processed -> realtime_stats + user_behavior")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
