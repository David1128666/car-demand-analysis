package com.car.analysis.offline.analysis

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{SaveMode, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

object MarketInsightAnalysis {

  def run(spark: SparkSession): Unit = {
    val props = getProps()

    brandRank(spark, props)           // 1. 品牌偏好排行 Top5
    marketShare(spark, props)         // 2. 品牌市占率变化
    keywordStats(spark, props)        // 3. 搜索关键词统计
    priceWarAlert(spark, props)       // 4. 价格战监测
    priceChangeReason(spark, props)   // 5. 价格变动原因统计
    fuelTypeTrend(spark, props)       // 6. 燃油类型趋势
    newTrending(spark, props)         // 7. 新车关注度排行
  }

  def brandRank(spark: SparkSession, props: java.util.Properties): Unit = {
    import spark.implicits._
    val statsDF = spark.read.jdbc(AppConfig.MySQL.url, "realtime_stats", props)

    val brandAgg = statsDF
      .filter($"stats_type".startsWith("beh_") 
        && $"target_name".isNotNull 
        && $"target_name" =!= "global_search"
        && length($"target_name") > 0
        && !$"target_name".like("??%")
        && $"target_name".notEqual("?")
        && !$"target_name".rlike("^[0-9]+$"))
      .groupBy("target_id", "target_name", "stats_date")
      .agg(sum("pv").as("pv"), sum("uv").as("uv"))

    val windowSpec = Window.partitionBy("stats_date").orderBy($"pv".desc)
    val top5 = brandAgg
      .withColumn("rank_pos", row_number().over(windowSpec))
      .filter($"rank_pos" <= 5)
      .select($"target_id".as("brand_id"), $"target_name".as("brand_name"),
        $"pv", $"uv", $"rank_pos", $"stats_date")

    top5.write.mode("overwrite").jdbc(AppConfig.MySQL.url, "region_brand_rank", props)
    println(s"[MarketInsight] Brand rank:  rows")
  }

  def marketShare(spark: SparkSession, props: java.util.Properties): Unit = {
    import spark.implicits._
    val statsDF = spark.read.jdbc(AppConfig.MySQL.url, "realtime_stats", props)

    val filteredStats = statsDF
      .filter($"stats_type".startsWith("beh_")
        && $"target_name".isNotNull
        && $"target_name" =!= "global_search"
        && length($"target_name") > 0
        && !$"target_name".like("??%")
        && $"target_name".notEqual("?")
        && !$"target_name".rlike("^[0-9]+$"))
    val dailyTotal = filteredStats.groupBy("stats_date").agg(sum("pv").as("total_pv"))
    val brandDaily = filteredStats
      .groupBy("target_id", "target_name", "stats_date")
      .agg(sum("pv").as("pv"))

    val shareDF = brandDaily
      .join(dailyTotal, Seq("stats_date"))
      .withColumn("share_pct", round($"pv" * 100.0 / $"total_pv", 2))
      .select($"target_id".as("brand_id"), $"target_name".as("brand_name"),
        $"pv", $"share_pct", $"stats_date")

    shareDF.write.mode("overwrite").jdbc(AppConfig.MySQL.url, "market_share", props)
    println(s"[MarketInsight] Market share:  rows")
  }

  def keywordStats(spark: SparkSession, props: java.util.Properties): Unit = {
    import spark.implicits._
    val searchDF = spark.read.jdbc(AppConfig.MySQL.url, "search_log", props)

    val keywordAgg = searchDF
      .filter($"keyword".isNotNull && $"keyword" =!= "")
      .groupBy("keyword")
      .agg(count("*").as("search_count"), countDistinct("user_id").as("unique_users"))
      .withColumn("stats_date", current_date())
      .select("keyword", "search_count", "unique_users", "stats_date")

    keywordAgg.write.mode("overwrite").jdbc(AppConfig.MySQL.url, "keyword_stats", props)
    println(s"[MarketInsight] Keyword stats:  rows")
  }

  def priceWarAlert(spark: SparkSession, props: java.util.Properties): Unit = {
    import spark.implicits._
    val priceDF = spark.read.jdbc(AppConfig.MySQL.url, "realtime_price_stats", props)

    val warDF = priceDF
      .groupBy("brand_id", "brand_name", "car_type")
      .agg(
        round(avg("avg_discount_rate"), 4).as("avg_discount_7d"),
        round(avg("avg_discount_rate"), 4).as("avg_discount_14d")
      )
      .withColumn("discount_change", round(coalesce($"avg_discount_7d", lit(0)) * 100, 2))
      .withColumn("alert_level",
        when($"avg_discount_7d" >= 0.15, lit("high"))
          .when($"avg_discount_7d" >= 0.08, lit("medium"))
          .otherwise(lit("normal")))
      .withColumn("stats_date", current_date())
      .filter($"avg_discount_7d".isNotNull)
      .select("brand_id", "brand_name", "car_type", "avg_discount_7d",
        "avg_discount_14d", "discount_change", "alert_level", "stats_date")

    warDF.write.mode("overwrite").jdbc(AppConfig.MySQL.url, "price_war_alert", props)
    println(s"[MarketInsight] Price war alert:  rows")
  }

  def priceChangeReason(spark: SparkSession, props: java.util.Properties): Unit = {
    import spark.implicits._
    val priceDF = spark.read.jdbc(AppConfig.MySQL.url, "realtime_price_stats", props)

    val reasonAgg = priceDF
      .filter($"price_change_reason".isNotNull && $"price_change_reason" =!= "")
      .groupBy("price_change_reason")
      .agg(
        count("*").as("occurrence_count"),
        round(avg("avg_discount_rate"), 4).as("avg_discount"),
        sum("quote_count").as("affected_quotes")
      )
      .withColumn("stats_date", current_date())
      .select("price_change_reason", "occurrence_count", "avg_discount", "affected_quotes", "stats_date")

    reasonAgg.write.mode("overwrite").jdbc(AppConfig.MySQL.url, "price_change_reason_stats", props)
    println(s"[MarketInsight] Price change reason:  rows")
  }

  def fuelTypeTrend(spark: SparkSession, props: java.util.Properties): Unit = {
    import spark.implicits._
    val statsDF = spark.read.jdbc(AppConfig.MySQL.url, "realtime_stats", props)

    val fuelAgg = statsDF
      .filter($"stats_type".startsWith("beh_")
        && $"fuel_type".isNotNull && $"fuel_type" =!= "None" && $"fuel_type" =!= "")
      .groupBy("fuel_type", "stats_date")
      .agg(sum("pv").as("pv"), sum("uv").as("uv"))
      .select("fuel_type", "pv", "uv", "stats_date")

    fuelAgg.write.mode("overwrite").jdbc(AppConfig.MySQL.url, "fuel_type_trend", props)
    println(s"[MarketInsight] Fuel type trend:  rows")
  }

  def newTrending(spark: SparkSession, props: java.util.Properties): Unit = {
    import spark.implicits._
    val statsDF = spark.read.jdbc(AppConfig.MySQL.url, "realtime_stats", props)
    val carInfoDF = spark.read.jdbc(AppConfig.MySQL.url, "car_info", props)

    val carActivity = statsDF
      .filter($"stats_type".startsWith("beh_")
        && !$"target_name".like("??%")
        && $"target_name".notEqual("?")
        && !$"target_name".rlike("^[0-9]+$"))
      .groupBy("target_name")
      .agg(
        sum("pv").as("total_pv"),
        sum("uv").as("total_uv"),
        sum("collect_count").as("total_collect"),
        sum("consult_count").as("total_consult")
      )

    val trending = carInfoDF
      .filter($"is_on_sale" === 1)
      .join(carActivity, carInfoDF("brand_name") === carActivity("target_name"), "left")
      .na.fill(0, Seq("total_pv", "total_uv", "total_collect", "total_consult"))
      .withColumn("hot_score", round(
        coalesce($"total_pv", lit(0)) * 0.4 +
        coalesce($"total_uv", lit(0)) * 0.3 +
        coalesce($"total_collect", lit(0)) * 0.2 +
        coalesce($"total_consult", lit(0)) * 0.1, 2))
      .withColumn("stats_date", current_date())
      .orderBy($"hot_score".desc)
      .limit(20)
      .select("car_id", "brand_id", "brand_name", "series_name", "model_name",
        "car_type", "fuel_type", "price", "hot_score", "total_pv", "total_uv",
        "total_collect", "total_consult", "stats_date")

    trending.write.mode("overwrite").jdbc(AppConfig.MySQL.url, "new_trending", props)
    println(s"[MarketInsight] New trending:  rows")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
