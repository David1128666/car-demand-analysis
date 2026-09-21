from database import query, query_one, get_system_config_int
from cache_utils import cached


def get_overview():
    def fetch():
        return query_one("""
            SELECT
                COALESCE(SUM(pv), 0) AS total_pv,
                COALESCE(SUM(uv), 0) AS total_uv,
                COALESCE(SUM(search_count), 0) AS search_count,
                COALESCE(SUM(consult_count), 0) AS consult_count,
                COALESCE(SUM(collect_count), 0) AS collect_count,
                (SELECT COUNT(*) FROM car_info WHERE is_on_sale = 1)
                + (SELECT COUNT(*) FROM admin_added_cars WHERE is_on_sale = 1) AS car_count,
                COALESCE(COUNT(DISTINCT target_id), 0) AS total_users
            FROM realtime_stats
            WHERE stats_date = CURDATE()
              AND target_name IS NOT NULL
              AND target_name NOT REGEXP '^[0-9]+$'
              AND HEX(target_name) NOT LIKE 'E59381E7898C%'
              AND HEX(target_name) NOT LIKE '3F3F3F3F%'
        """)
    ttl = get_system_config_int("sys.cache.realtime.ttl", 30)
    return cached("dashboard:overview", ttl, fetch)


def get_realtime_stats():
    def fetch():
        return query("""
            SELECT stats_type, target_id, target_name, pv, uv,
                   search_count, consult_count, collect_count,
                   stats_date, stats_hour, IFNULL(stats_minute, '00') AS stats_minute
            FROM realtime_stats
            WHERE target_name IS NOT NULL
              AND target_name != 'global_search'
              AND target_name NOT REGEXP '^[0-9]+$'
              AND target_name NOT LIKE '%s%%'
              AND HEX(target_name) NOT LIKE '3F3F3F3F%%'
            ORDER BY stats_date DESC, stats_hour DESC, IFNULL(stats_minute, '00') DESC
            LIMIT 200
        """ % '品牌')
    ttl = get_system_config_int("sys.cache.realtime.ttl", 30)
    return cached("dashboard:realtime", ttl, fetch)


def get_price_stats(brand_id=None, car_type=None, start_date=None, end_date=None):
    conditions = ["p.stat_hour >= DATE_FORMAT(CURDATE(), '%%Y%%m%%d%%H%%i')"]
    params = []
    if brand_id:
        conditions.append("p.brand_id = %s")
        params.append(brand_id)
    if car_type:
        conditions.append("p.car_type = %s")
        params.append(car_type)
    if start_date:
        conditions.append("p.window_end >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("p.window_end <= %s")
        params.append(end_date)
    sql = f"""
        SELECT COALESCE(c.brand_name, p.brand_name) AS brand_name,
               p.car_type,
               ROUND(AVG(p.avg_original_price), 1) AS avg_original_price,
               ROUND(AVG(p.avg_quoted_price), 1) AS avg_quoted_price,
               ROUND(AVG(p.avg_discount_rate) * 100, 0) AS discount_pct,
               SUM(p.quote_count) AS quote_count,
               MAX(p.stat_hour) AS stat_hour,
               SUBSTRING_INDEX(
                   GROUP_CONCAT(DISTINCT p.top_promotion SEPARATOR '|||'), '|||', 3
               ) AS top_promotion
        FROM realtime_price_stats p
        LEFT JOIN (SELECT DISTINCT brand_id, brand_name FROM car_info) c ON p.brand_id = c.brand_id
        WHERE HEX(p.brand_name) NOT LIKE 'E59381E7898C%%'
          AND {' AND '.join(conditions)}
        GROUP BY COALESCE(c.brand_name, p.brand_name), p.car_type
        ORDER BY SUM(p.quote_count) DESC
        LIMIT 100
    """
    rows = query(sql, params)
    for row in rows:
        if row.get("top_promotion"):
            row["top_promotion"] = row["top_promotion"].replace("|||", "、")
    return rows


def get_loan_stats(brand_id=None, car_type=None, loan_type=None, start_date=None, end_date=None):
    conditions = ["1=1"]
    params = []
    if brand_id:
        conditions.append("l.brand_id = %s")
        params.append(brand_id)
    if car_type:
        conditions.append("l.car_type = %s")
        params.append(car_type)
    if loan_type:
        conditions.append("l.loan_type = %s")
        params.append(loan_type)
    if start_date:
        conditions.append("l.window_end >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("l.window_end <= %s")
        params.append(end_date)
    sql = f"""
        SELECT l.stat_hour, l.brand_id, l.car_type, l.loan_type,
               l.avg_car_price, l.avg_loan_amount, l.avg_interest_rate,
               l.avg_monthly_payment, l.inquiry_count, l.approval_rate
        FROM realtime_loan_stats l
        WHERE {' AND '.join(conditions)}
        ORDER BY l.window_end DESC LIMIT 100
    """
    return query(sql, params)


def get_finance_summary():
    def fetch():
        return query_one("""
            SELECT
                (SELECT COALESCE(AVG(avg_car_price), 0) FROM (SELECT avg_car_price FROM realtime_loan_stats ORDER BY window_end DESC LIMIT 100) t) AS avg_car_price,
                (SELECT COALESCE(AVG(avg_loan_amount), 0) FROM (SELECT avg_loan_amount FROM realtime_loan_stats ORDER BY window_end DESC LIMIT 100) t) AS avg_loan_amount,
                (SELECT COALESCE(AVG(avg_interest_rate), 0) FROM (SELECT avg_interest_rate FROM realtime_loan_stats ORDER BY window_end DESC LIMIT 100) t) AS avg_rate,
                (SELECT COALESCE(SUM(inquiry_count), 0) FROM (SELECT inquiry_count FROM realtime_loan_stats ORDER BY window_end DESC LIMIT 100) t) AS total_inquiries,
                (SELECT COALESCE(AVG(avg_discount_rate) * 100, 0) FROM (SELECT avg_discount_rate FROM realtime_price_stats ORDER BY window_end DESC LIMIT 100) t) AS avg_discount,
                (SELECT COALESCE(SUM(quote_count), 0) FROM (SELECT quote_count FROM realtime_price_stats ORDER BY window_end DESC LIMIT 100) t) AS total_quotes
        """)
    ttl = get_system_config_int("sys.cache.realtime.ttl", 30)
    return cached("dashboard:finance", ttl, fetch)
