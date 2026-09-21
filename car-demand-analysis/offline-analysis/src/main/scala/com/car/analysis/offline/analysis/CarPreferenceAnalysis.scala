package com.car.analysis.offline.analysis

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{SaveMode, SparkSession}
import org.apache.spark.sql.functions._

object CarPreferenceAnalysis {

  def run(spark: SparkSession): Unit = {
    import spark.implicits._
    val props = getProps()

    val behaviorDF = spark.read.jdbc(AppConfig.MySQL.url, "user_behavior", props)
    val carInfoDF = spark.read.jdbc(AppConfig.MySQL.url, "car_info", props)

    val carPref = behaviorDF
      .join(carInfoDF, Seq("car_id"), "left")
      .groupBy($"car_type", $"fuel_type")
      .agg(
        count("*").as("interact_count"),
        countDistinct("user_id").as("unique_users")
      )
      .orderBy($"interact_count".desc)

    println("=== 车型偏好排行 ===")
    carPref.show(20, truncate = false)

    val brandPref = behaviorDF
      .join(carInfoDF, Seq("car_id"), "left")
      .groupBy($"brand_name")
      .agg(
        count("*").as("total_views"),
        countDistinct("user_id").as("unique_users"),
        countDistinct("car_id").as("car_variety")
      )
      .orderBy($"total_views".desc)
      .limit(10)

    println("=== 品牌热度排行 Top 10 ===")
    brandPref.show(10, truncate = false)

    println(s"[CarPreferenceAnalysis] Done")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
