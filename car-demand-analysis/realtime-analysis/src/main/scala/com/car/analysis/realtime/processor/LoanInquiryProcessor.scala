package com.car.analysis.realtime.processor

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import java.sql.Timestamp

object LoanInquiryProcessor {

  def process(df: DataFrame, spark: SparkSession, batchId: Long): Unit = {
    import spark.implicits._
    val props = getProps()

    val windowEnd = new Timestamp(System.currentTimeMillis())
    val windowStart = new Timestamp(System.currentTimeMillis() - 600000)

    val result = df
      .filter($"brand_id".isNotNull && $"car_type".isNotNull && $"loan_type".isNotNull)
      .groupBy(
        concat(date_format(current_timestamp(), "yyyyMMddHHmm"), lpad(floor(second(current_timestamp()) / 10) * 10, 2, "0")).as("stat_hour_v"),
        $"brand_id", $"car_type", $"loan_type")
      .agg(
        round(avg("car_price"), 2).as("avg_car_price"),
        round(avg("loan_amount"), 2).as("avg_loan_amount"),
        round(avg("interest_rate"), 2).as("avg_interest_rate"),
        round(avg("monthly_payment"), 2).as("avg_monthly_payment"),
        count("*").as("inquiry_count"),
        round(
          sum(when($"loan_status".equalTo("已放款"), 1L).otherwise(0L)) * 100.0 /
            greatest(count("*"), lit(1L)), 2
        ).as("approval_rate"),
        round(avg("credit_score"), 0).as("avg_credit_score")
      )
      .select(
        $"stat_hour_v".as("stat_hour"),
        lit(windowStart).as("window_start"),
        lit(windowEnd).as("window_end"),
        $"brand_id", $"car_type", $"loan_type",
        $"avg_car_price", $"avg_loan_amount", $"avg_interest_rate", $"avg_monthly_payment",
        $"inquiry_count", $"approval_rate", $"avg_credit_score",
        current_timestamp().as("realtime_timestamp")
      )

    result.write.mode("append").jdbc(AppConfig.MySQL.url, "realtime_loan_stats", props)
    println(s"[Batch $batchId] car-loan-inquiry: processed -> realtime_loan_stats")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
