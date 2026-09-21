package com.car.analysis.realtime

import com.car.analysis.common.config.AppConfig
import com.car.analysis.realtime.processor._
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.types._

object RealTimeAnalysisApp {

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName(s"${AppConfig.Spark.appName}-Realtime")
      .master(AppConfig.Spark.master)
      .config("spark.sql.adaptive.enabled", "false")
      .config("spark.sql.shuffle.partitions", "4")
      .config("spark.streaming.kafka.maxRatePerPartition", "500")
      .config("spark.streaming.stopGracefullyOnShutdown", "true")
      .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    try {
      val kafkaBootstrap = AppConfig.Kafka.bootstrapServers

      startStream(spark, kafkaBootstrap, AppConfig.Kafka.Topics.userBehavior,
        userBehaviorSchema, UserBehaviorProcessor.process)

      startStream(spark, kafkaBootstrap, AppConfig.Kafka.Topics.carSearch,
        carSearchSchema, SearchStatsProcessor.process)

      startStream(spark, kafkaBootstrap, AppConfig.Kafka.Topics.carConsult,
        carConsultSchema, ConsultStatsProcessor.process)

      startStream(spark, kafkaBootstrap, AppConfig.Kafka.Topics.carPriceQuote,
        carPriceQuoteSchema, PriceQuoteProcessor.process)

      startStream(spark, kafkaBootstrap, AppConfig.Kafka.Topics.carLoanInquiry,
        carLoanInquirySchema, LoanInquiryProcessor.process)

      println(">>> RealTime Analysis started. Waiting for Kafka data...")
      spark.streams.awaitAnyTermination()

    } finally {
      spark.stop()
    }
  }

  private def startStream(spark: SparkSession, bootstrap: String, topic: String,
                          schema: StructType, processor: (DataFrame, SparkSession, Long) => Unit): Unit = {
    spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", bootstrap)
      .option("subscribe", topic)
      .option("startingOffsets", AppConfig.Kafka.autoOffsetReset)
      .option("failOnDataLoss", "false")
      .option("maxOffsetsPerTrigger", "500")
      .load()
      .select(from_json(col("value").cast(StringType), schema).as("data"))
      .select("data.*")
      .writeStream
      .trigger(Trigger.ProcessingTime("10 seconds"))
      .option("checkpointLocation", s"${AppConfig.Spark.checkpointDir}/$topic")
      .foreachBatch { (batchDF: DataFrame, batchId: Long) =>
        if (!batchDF.isEmpty) {
          batchDF.cache()
          processor(batchDF, spark, batchId)
          batchDF.unpersist()
        }
        ()
      }
      .start()
  }

  private val userBehaviorSchema: StructType = new StructType()
    .add("behavior_id", StringType)
    .add("user_id", StringType)
    .add("car_id", LongType)
    .add("behavior_type", StringType)
    .add("behavior_time", StringType)
    .add("brand_id", LongType)
    .add("brand_name", StringType)
    .add("series_id", LongType)
    .add("car_type", StringType)
    .add("fuel_type", StringType)
    .add("price", DoubleType)
    .add("region_id", LongType)
    .add("session_id", StringType)
    .add("search_keyword", StringType)

  private val carSearchSchema: StructType = new StructType()
    .add("search_id", StringType)
    .add("user_id", StringType)
    .add("search_keyword", StringType)
    .add("search_time", StringType)
    .add("region_id", LongType)
    .add("result_count", LongType)
    .add("click_position", LongType)

  private val carConsultSchema: StructType = new StructType()
    .add("consult_id", StringType)
    .add("user_id", StringType)
    .add("car_id", LongType)
    .add("consult_time", StringType)
    .add("consult_type", StringType)
    .add("region_id", LongType)
    .add("has_phone", BooleanType)
    .add("followup_status", StringType)

  private val carPriceQuoteSchema: StructType = new StructType()
    .add("quote_id", StringType)
    .add("car_id", LongType)
    .add("brand_id", LongType)
    .add("brand_name", StringType)
    .add("series_id", LongType)
    .add("car_type", StringType)
    .add("original_price", DoubleType)
    .add("quoted_price", DoubleType)
    .add("discount_rate", DoubleType)
    .add("price_change_reason", StringType)
    .add("region_id", LongType)
    .add("dealer_id", StringType)
    .add("quote_time", StringType)
    .add("validity_period", LongType)
    .add("promotion_info", StringType)

  private val carLoanInquirySchema: StructType = new StructType()
    .add("loan_id", StringType)
    .add("user_id", StringType)
    .add("car_id", LongType)
    .add("brand_id", LongType)
    .add("car_type", StringType)
    .add("loan_type", StringType)
    .add("car_price", DoubleType)
    .add("down_payment", DoubleType)
    .add("loan_amount", DoubleType)
    .add("loan_term", LongType)
    .add("interest_rate", DoubleType)
    .add("monthly_payment", DoubleType)
    .add("region_id", LongType)
    .add("credit_score", LongType)
    .add("inquiry_time", StringType)
    .add("loan_status", StringType)
    .add("has_insurance", BooleanType)
    .add("preferred_bank", StringType)
}