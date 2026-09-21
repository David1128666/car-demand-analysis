package com.car.analysis.common.config

import com.typesafe.config.{Config, ConfigFactory}

object AppConfig {
  private val config: Config = ConfigFactory.load()

  object Kafka {
    val bootstrapServers: String = config.getString("kafka.bootstrap.servers")
    val groupId: String = config.getString("kafka.group.id")
    val autoOffsetReset: String = config.getString("kafka.auto.offset.reset")

    object Topics {
      val userBehavior: String = config.getString("kafka.topics.user-behavior")
      val carSearch: String = config.getString("kafka.topics.car-search")
      val carConsult: String = config.getString("kafka.topics.car-consult")
      val carPriceQuote: String = config.getString("kafka.topics.car-price-quote")
      val carLoanInquiry: String = config.getString("kafka.topics.car-loan-inquiry")
    }
  }

  object MySQL {
    val url: String = config.getString("mysql.url")
    val user: String = config.getString("mysql.user")
    val password: String = config.getString("mysql.password")
    val driver: String = config.getString("mysql.driver")
  }

  object Spark {
    val appName: String = config.getString("spark.app.name")
    val master: String = config.getString("spark.master")
    val streamingBatchDuration: Int = config.getInt("spark.streaming.batch.duration.seconds")
    val checkpointDir: String = config.getString("spark.checkpoint.dir")
  }
}
