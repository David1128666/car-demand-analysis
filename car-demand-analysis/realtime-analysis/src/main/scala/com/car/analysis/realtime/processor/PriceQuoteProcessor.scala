package com.car.analysis.realtime.processor

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import java.sql.Timestamp

object PriceQuoteProcessor {

  def process(df: DataFrame, spark: SparkSession, batchId: Long): Unit = {
    import spark.implicits._
    val props = getProps()

    val windowEnd = new Timestamp(System.currentTimeMillis())
    val windowStart = new Timestamp(System.currentTimeMillis() - 600000)

    val result = df
      .filter($"brand_id".isNotNull && !$"brand_name".startsWith("??"))
      .groupBy(
        concat(date_format(current_timestamp(), "yyyyMMddHHmm"), lpad(floor(second(current_timestamp()) / 10) * 10, 2, "0")).as("stat_hour_v"),
        $"brand_id", $"brand_name", $"car_type")
      .agg(
        round(avg("original_price"), 2).as("avg_original_price"),
        round(avg("quoted_price"), 2).as("avg_quoted_price"),
        round(avg("discount_rate"), 4).as("avg_discount_rate"),
        count("*").as("quote_count"),
        sum(when($"promotion_info".isNotNull && length($"promotion_info") > 0, 1L).otherwise(0L)).as("promotion_count"),
        first($"promotion_info", true).as("top_promotion"),
        first($"price_change_reason", true).as("price_change_reason")
      )
      .select(
        $"stat_hour_v".as("stat_hour"),
        lit(windowStart).as("window_start"),
        lit(windowEnd).as("window_end"),
        $"brand_id", $"brand_name", $"car_type",
        $"avg_original_price", $"avg_quoted_price", $"avg_discount_rate",
        $"quote_count", $"promotion_count", $"top_promotion",
        $"price_change_reason",
        current_timestamp().as("realtime_timestamp")
      )

    result.write.mode("append").jdbc(AppConfig.MySQL.url, "realtime_price_stats", props)

    println(s"[Batch $batchId] car-price-quote: processed -> realtime_price_stats")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
