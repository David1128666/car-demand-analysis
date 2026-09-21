package com.car.analysis.offline.analysis

import com.car.analysis.common.config.AppConfig
import org.apache.spark.sql.{SparkSession}
import org.apache.spark.sql.functions._

object UserProfileAnalysis {

  def run(spark: SparkSession): Unit = {
    import spark.implicits._
    val props = getProps()

    val behaviorDF = spark.read.jdbc(AppConfig.MySQL.url, "user_behavior", props)

    val profileStats = behaviorDF
      .groupBy("user_id")
      .agg(
        count("*").as("total_events"),
        sum(when($"behavior_type" === "search", 1).otherwise(0)).as("search_count"),
        sum(when($"behavior_type" === "consult", 1).otherwise(0)).as("consult_count"),
        sum(when($"behavior_type" === "collect", 1).otherwise(0)).as("collect_count"),
        sum(when($"behavior_type" === "browse", 1).otherwise(0)).as("browse_count"),
        round(
          sum(when($"behavior_type" === "search", 1).otherwise(0)) * 0.3 +
          sum(when($"behavior_type" === "consult", 1).otherwise(0)) * 0.4 +
          sum(when($"behavior_type" === "collect", 1).otherwise(0)) * 0.2 +
          sum(when($"behavior_type" === "browse", 1).otherwise(0)) * 0.1, 2
        ).as("user_score")
      )
      .orderBy($"user_score".desc)

    println("=== 用户活跃度画像 ===")
    profileStats.show(20, truncate = false)

    println(s"[UserProfileAnalysis] ${profileStats.count()} users analyzed")
  }

  private def getProps(): java.util.Properties = {
    val p = new java.util.Properties()
    p.setProperty("user", AppConfig.MySQL.user)
    p.setProperty("password", AppConfig.MySQL.password)
    p.setProperty("driver", AppConfig.MySQL.driver)
    p
  }
}
