from database import query, query_one, get_system_config_int
from cache_utils import cached


def get_daily_trend():
    def fetch():
        return query("""
            SELECT stats_type, stats_date,
                   SUM(pv) AS total_pv, SUM(uv) AS total_uv,
                   SUM(search_count) AS total_search,
                   SUM(consult_count) AS total_consult,
                   SUM(collect_count) AS total_collect
            FROM daily_stats
            WHERE target_name IS NOT NULL
              AND target_name != 'global_search'
              AND target_name NOT REGEXP '^[0-9]+$'
              AND HEX(target_name)  NOT LIKE 'E59381E7898C%'
              AND HEX(target_name) NOT LIKE '3F3F3F3F%'
            GROUP BY stats_type, stats_date
            ORDER BY stats_date DESC
            LIMIT 50
        """)
    ttl = get_system_config_int("sys.cache.trends.ttl", 3600)
    return cached("analysis:daily_trend", ttl, fetch)


def get_brand_popularity():
    def fetch():
        return query("""
            SELECT brand_id, brand_name, uv, pv, search_count, consult_count, collect_count
            FROM v_brand_popularity
            ORDER BY pv DESC
            LIMIT 20
        """)
    ttl = get_system_config_int("sys.cache.trends.ttl", 3600)
    return cached("analysis:brand_popularity", ttl, fetch)

def get_user_behavior_stats():
    sql = """
        SELECT user_id, behavior_date, behavior_type,
               behavior_count, session_count, car_count
        FROM v_user_behavior_stats
        ORDER BY behavior_date DESC, behavior_count DESC
        LIMIT 100
    """
    return query(sql)

def get_recommendation_stats():
    # Hierarchical partition: each recommendation falls into exactly ONE tier
    #   convert: user consulted / collected the car (highest intent)
    #   click:   user searched / browsed (active), but didn't convert
    #   expose:  everything else — rec exists but no active engagement
    # Guarantees: total = expose + click + convert  (rates sum to 100%)
    sql = """
        SELECT rec_type,
               COUNT(*) AS total_count,
               SUM(CASE WHEN tier = 'expose'  THEN 1 ELSE 0 END) AS exposure_count,
               SUM(CASE WHEN tier = 'click'   THEN 1 ELSE 0 END) AS click_count,
               SUM(CASE WHEN tier = 'convert' THEN 1 ELSE 0 END) AS convert_count,
               ROUND(SUM(CASE WHEN tier = 'expose'  THEN 1 ELSE 0 END) * 100.0
                     / NULLIF(COUNT(*), 0), 1) AS exposure_rate,
               ROUND(SUM(CASE WHEN tier = 'click'   THEN 1 ELSE 0 END) * 100.0
                     / NULLIF(COUNT(*), 0), 1) AS click_rate,
               ROUND(SUM(CASE WHEN tier = 'convert' THEN 1 ELSE 0 END) * 100.0
                     / NULLIF(COUNT(*), 0), 1) AS convert_rate
        FROM (
            SELECT r.rec_type,
                   CASE
                       WHEN ub.intent_beh > 0 THEN 'convert'
                       WHEN ub.active_beh > 0 THEN 'click'
                       ELSE 'expose'
                   END AS tier
            FROM recommendation r
            JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1
            LEFT JOIN (
                SELECT user_id, car_id,
                       MAX(CASE WHEN behavior_type IN ('consult','collect') THEN 1 ELSE 0 END) AS intent_beh,
                       MAX(CASE WHEN behavior_type IN ('search','browse')   THEN 1 ELSE 0 END) AS active_beh
                FROM user_behavior WHERE car_id > 0
                GROUP BY user_id, car_id
            ) ub ON r.user_id = ub.user_id AND r.car_id = ub.car_id
        ) t
        GROUP BY rec_type
    """

    real_stats = query(sql)

    # Ensure all 3 active strategies appear
    rec_types = ['collaborative', 'content_based', 'hot']
    existing = {r["rec_type"] for r in real_stats}
    result = list(real_stats)
    for t in rec_types:
        if t not in existing:
            result.append({
                "rec_type": t,
                "total_count": 0, "exposure_count": 0, "click_count": 0,
                "convert_count": 0, "exposure_rate": 0, "click_rate": 0,
                "convert_rate": 0,
            })

    # Compute hybrid = aggregate across all strategies (cast Decimal -> int)
    hybrid_total = sum(int(r["total_count"]) for r in result)
    hybrid_expose = sum(int(r["exposure_count"]) for r in result)
    hybrid_click = sum(int(r["click_count"]) for r in result)
    hybrid_convert = sum(int(r["convert_count"]) for r in result)
    result.append({
        "rec_type": "hybrid",
        "total_count": hybrid_total,
        "exposure_count": hybrid_expose,
        "click_count": hybrid_click,
        "convert_count": hybrid_convert,
        "exposure_rate": round(hybrid_expose * 100.0 / max(hybrid_total, 1), 1),
        "click_rate": round(hybrid_click * 100.0 / max(hybrid_total, 1), 1),
        "convert_rate": round(hybrid_convert * 100.0 / max(hybrid_total, 1), 1),
    })

    return result

def get_car_type_preference():
    sql = """
        SELECT car_type,
               SUM(pv) AS total_pv,
               SUM(uv) AS total_uv,
               COUNT(DISTINCT target_id) AS brand_count
        FROM realtime_stats
        WHERE stats_type LIKE 'beh_%%'
          AND car_type IS NOT NULL AND car_type != ''
          AND HEX(target_name) NOT LIKE 'E59381E7898C%'
          AND stats_date = CURDATE()
        GROUP BY car_type
        ORDER BY total_pv DESC
    """
    return query(sql)

def get_brand_consult_rate():
    sql = """
        SELECT target_name AS brand_name, SUM(consult_count) AS total_consult,
               SUM(pv) AS total_pv,
               ROUND(SUM(consult_count)*100.0/GREATEST(SUM(pv),1), 2) AS consult_rate,
               SUM(search_count) AS total_search
        FROM realtime_stats
        WHERE stats_type LIKE 'beh_%%'
          AND HEX(target_name) NOT LIKE 'E59381E7898C%'
          AND target_name IS NOT NULL
          AND stats_date = CURDATE()
        GROUP BY target_name
        HAVING SUM(pv) > 0
        ORDER BY consult_rate DESC
    """
    return query(sql)

def get_loan_approval_rate():
    sql = """
        SELECT loan_type,
               ROUND(AVG(approval_rate), 1) AS avg_approval_rate,
               COUNT(*) AS inquiry_count,
               ROUND(AVG(avg_loan_amount), 1) AS avg_loan_amount,
               ROUND(AVG(avg_monthly_payment), 1) AS avg_monthly_payment
        FROM realtime_loan_stats
        WHERE stat_hour >= DATE_FORMAT(CURDATE(), '%%Y%%m%%d%%H%%i')
        GROUP BY loan_type
        ORDER BY avg_approval_rate DESC
    """
    return query(sql)

def get_user_profile(user_id: str = None):
    if user_id:
        sql = "SELECT * FROM user_profile WHERE user_id = %s"
        return query(sql, (user_id,))
    else:
        sql = "SELECT * FROM user_profile ORDER BY score DESC LIMIT 50"
        return query(sql)
