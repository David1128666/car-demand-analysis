from database import query, query_one

# 1. 品牌偏好排行 Top5
def get_brand_rank():
    sql = """
        SELECT brand_id, brand_name, pv, uv, rank_pos, stats_date
        FROM region_brand_rank
        ORDER BY stats_date DESC, rank_pos ASC
        LIMIT 20
    """
    return query(sql)

# 2. 品牌市占率变化
def get_market_share():
    sql = """
        SELECT brand_id, brand_name, pv, share_pct, stats_date
        FROM market_share
        ORDER BY stats_date DESC, share_pct DESC
        LIMIT 30
    """
    return query(sql)

# 3. 搜索关键词云
def get_keyword_cloud():
    sql = """
        SELECT keyword, search_count, unique_users, stats_date
        FROM keyword_stats
        ORDER BY search_count DESC
        LIMIT 50
    """
    return query(sql)

# 4. 价格战监测
def get_price_war():
    sql = """
        SELECT brand_id, brand_name, car_type,
               CAST(avg_discount_7d AS DECIMAL(6,2)) AS avg_discount_pct,
               CAST(avg_discount_14d AS DECIMAL(6,2)) AS avg_discount_14d_pct,
               discount_change, alert_level, stats_date
        FROM price_war_alert WHERE HEX(brand_name) NOT LIKE '3F3F3F3F%'
        ORDER BY avg_discount_7d DESC
        LIMIT 20
    """
    return query(sql)

# 5. 价格变动原因统计
def get_price_reasons():
    sql = """
        SELECT price_change_reason, occurrence_count,
               ROUND(avg_discount * 100, 1) AS avg_discount_pct,
               affected_quotes, stats_date
        FROM price_change_reason_stats
        ORDER BY occurrence_count DESC
    """
    return query(sql)

# 6. 燃油类型趋势
def get_fuel_trend():
    sql = """
        SELECT fuel_type, SUM(pv) AS total_pv, SUM(uv) AS total_uv, MAX(stats_date) AS latest_date
        FROM fuel_type_trend
        GROUP BY fuel_type
        ORDER BY total_pv DESC
    """
    return query(sql)

# 7. 新车关注度排行


# 8. 品牌收藏率
def get_brand_collect_rate():
    """品牌收藏率排行"""
    sql = """
        SELECT target_name AS brand_name, SUM(pv) AS total_pv,
               SUM(collect_count) AS total_collect,
               ROUND(SUM(collect_count)*100.0/SUM(pv), 2) AS collect_rate,
               SUM(consult_count) AS total_consult,
               SUM(search_count) AS total_search
        FROM realtime_stats
        WHERE stats_type LIKE 'beh_%%'
          AND HEX(target_name) NOT LIKE 'E59381E7898C%'
          AND stats_date = CURDATE()
        GROUP BY target_name
        ORDER BY collect_rate DESC
    """
    return query(sql)

# 9. 促销效果分析
def get_promotion_effect():
    sql = """
        SELECT top_promotion AS promotion_name,
               COUNT(*) AS quote_count,
               ROUND(AVG(avg_discount_rate) * 100, 1) AS avg_discount_pct,
               SUM(promotion_count) AS promotion_total,
               COUNT(DISTINCT brand_id) AS brand_count
        FROM realtime_price_stats
        WHERE top_promotion IS NOT NULL AND top_promotion != ''
          AND stat_hour >= DATE_FORMAT(CURDATE(), '%%Y%%m%%d%%H%%i')
          AND HEX(brand_name) NOT LIKE 'E59381E7898C%'
          AND HEX(top_promotion) NOT LIKE 'E59381E7898C%'
        GROUP BY top_promotion
        ORDER BY quote_count DESC
        LIMIT 15
    """
    return query(sql)


# 10. 价格折扣分层
def get_discount_tiers():
    sql = """
        SELECT 
            CASE 
                WHEN avg_discount_rate >= 0.96 THEN '超高折扣(≥96%)'
                WHEN avg_discount_rate >= 0.93 THEN '高折扣(93-96%)'
                WHEN avg_discount_rate >= 0.90 THEN '中高折扣(90-93%)'
                WHEN avg_discount_rate >= 0.87 THEN '中折扣(87-90%)'
                ELSE '普通折扣(<87%)'
            END AS discount_range,
            COUNT(*) AS quote_count,
            ROUND(AVG(avg_discount_rate)*100, 1) AS avg_discount_pct,
            COUNT(DISTINCT brand_id) AS brand_count
        FROM realtime_price_stats
        WHERE HEX(brand_name) NOT LIKE 'E59381E7898C%'
          AND stat_hour >= DATE_FORMAT(CURDATE(), '%%Y%%m%%d%%H%%i')
        GROUP BY discount_range
        ORDER BY avg_discount_pct DESC
    """
    return query(sql)

def get_new_trending():
    sql = """
        SELECT car_id, brand_name, series_name, model_name,
               car_type, fuel_type, price, hot_score,
               total_pv, total_uv, total_collect, total_consult, stats_date
        FROM new_trending
        ORDER BY hot_score DESC
        LIMIT 20
    """
    return query(sql)

# 实时市占率（基于realtime_stats，按小时计算，只取最新6个时间段）
def get_realtime_market_share(brand_name: str = None):
    if brand_name:
        sql = """
            SELECT r.target_name AS brand_name,
                   r.stats_date,
                   r.stats_hour,
                   r.stats_minute,
                   r.brand_pv,
                   ROUND(r.brand_pv * 100.0 / t.total_pv, 2) AS share_pct
            FROM (
                SELECT target_name, stats_date, stats_hour,
                       IFNULL(stats_minute, '00') AS stats_minute,
                       SUM(pv) AS brand_pv
                FROM realtime_stats
                WHERE target_name = %s
                  AND stats_type LIKE 'beh_%%'
                GROUP BY target_name, stats_date, stats_hour, IFNULL(stats_minute, '00')
            ) r
            INNER JOIN (
                SELECT stats_date, stats_hour, IFNULL(stats_minute, '00') AS stats_minute
                FROM realtime_stats
                WHERE target_name = %s AND stats_type LIKE 'beh_%%'
                GROUP BY stats_date, stats_hour, IFNULL(stats_minute, '00')
                ORDER BY stats_date DESC, stats_hour DESC, stats_minute DESC
                LIMIT 6
            ) latest ON r.stats_date = latest.stats_date
                    AND r.stats_hour = latest.stats_hour
                    AND r.stats_minute = latest.stats_minute
            JOIN (
                SELECT stats_date, stats_hour,
                       IFNULL(stats_minute, '00') AS stats_minute,
                       SUM(pv) AS total_pv
                FROM realtime_stats
                WHERE target_name IS NOT NULL
                  AND stats_type LIKE 'beh_%%'
                  AND HEX(target_name) NOT LIKE 'E59381E7898C%%'
                  AND HEX(target_name) NOT LIKE '3F3F3F3F%%'
                GROUP BY stats_date, stats_hour, IFNULL(stats_minute, '00')
            ) t ON r.stats_date = t.stats_date
                AND r.stats_hour = t.stats_hour
                AND r.stats_minute = t.stats_minute
            ORDER BY r.stats_date DESC, r.stats_hour DESC, r.stats_minute DESC
        """
        return query(sql, (brand_name, brand_name))
    else:
        sql = """
            WITH latest_buckets AS (
                SELECT stats_date, stats_hour, IFNULL(stats_minute, '00') AS stats_minute
                FROM realtime_stats
                WHERE stats_type LIKE 'beh_%%'
                GROUP BY stats_date, stats_hour, IFNULL(stats_minute, '00')
                ORDER BY stats_date DESC, stats_hour DESC, stats_minute DESC
                LIMIT 6
            ),
            brand_pv AS (
                SELECT r.target_name AS brand_name,
                       r.stats_date, r.stats_hour,
                       IFNULL(r.stats_minute, '00') AS stats_minute,
                       SUM(r.pv) AS brand_pv
                FROM realtime_stats r
                JOIN latest_buckets lb
                  ON r.stats_date = lb.stats_date
                 AND r.stats_hour = lb.stats_hour
                 AND IFNULL(r.stats_minute, '00') = lb.stats_minute
                WHERE r.target_name IS NOT NULL
                  AND r.stats_type LIKE 'beh_%%'
                  AND HEX(r.target_name) NOT LIKE 'E59381E7898C%%'
                  AND HEX(r.target_name) NOT LIKE '3F3F3F3F%%'
                GROUP BY r.target_name, r.stats_date, r.stats_hour, IFNULL(r.stats_minute, '00')
            )
            SELECT b.brand_name, b.stats_date, b.stats_hour, b.stats_minute,
                   b.brand_pv,
                   ROUND(b.brand_pv * 100.0 / t.total_pv, 2) AS share_pct
            FROM brand_pv b
            JOIN (
                SELECT stats_date, stats_hour, stats_minute,
                       SUM(brand_pv) AS total_pv
                FROM brand_pv
                GROUP BY stats_date, stats_hour, stats_minute
            ) t ON b.stats_date = t.stats_date
                AND b.stats_hour = t.stats_hour
                AND b.stats_minute = t.stats_minute
            ORDER BY b.stats_date DESC, b.stats_hour DESC, b.stats_minute DESC,
                     b.brand_pv DESC
        """
        return query(sql)