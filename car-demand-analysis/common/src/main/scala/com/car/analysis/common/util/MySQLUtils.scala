package com.car.analysis.common.util

import java.sql.{Connection, DriverManager, PreparedStatement}
import com.car.analysis.common.config.AppConfig

object MySQLUtils {
  private var connection: Connection = _

  def getConnection: Connection = {
    if (connection == null || connection.isClosed) {
      Class.forName(AppConfig.MySQL.driver)
      connection = DriverManager.getConnection(
        AppConfig.MySQL.url,
        AppConfig.MySQL.user,
        AppConfig.MySQL.password
      )
    }
    connection
  }

  def executeUpdate(sql: String, params: Seq[Any]): Int = {
    val conn = getConnection
    val stmt = conn.prepareStatement(sql)
    try {
      params.zipWithIndex.foreach { case (param, idx) =>
        param match {
          case s: String => stmt.setString(idx + 1, s)
          case i: Int => stmt.setInt(idx + 1, i)
          case l: Long => stmt.setLong(idx + 1, l)
          case d: Double => stmt.setDouble(idx + 1, d)
          case b: Boolean => stmt.setBoolean(idx + 1, b)
          case _ => stmt.setObject(idx + 1, param)
        }
      }
      stmt.executeUpdate()
    } finally {
      stmt.close()
    }
  }

  def close(): Unit = {
    if (connection != null && !connection.isClosed) {
      connection.close()
    }
  }
}
