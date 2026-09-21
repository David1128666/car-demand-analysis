import random

from database import query, query_one, execute
from auth_utils import hash_password
from services.auth_service import list_users


# ── User Management ──


def create_user(username: str, password: str, nickname: str = None,
                role: str = "user", email: str = None, phone: str = None) -> dict:
    existing = query_one(
        "SELECT user_id FROM sys_user WHERE username = %s", (username,)
    )
    if existing:
        return {"success": False, "message": "用户名已存在"}
    pwd_hash = hash_password(password)
    user_id = execute(
        "INSERT INTO sys_user (username, password_hash, nickname, role, email, phone) "
        "VALUES (%s,%s,%s,%s,%s,%s)",
        (username, pwd_hash, nickname or username, role, email, phone)
    )
    return {"success": True, "message": "创建成功", "user_id": user_id}


def update_user_role(user_id: int, role: str) -> dict:
    execute("UPDATE sys_user SET role = %s WHERE user_id = %s", (role, user_id))
    return {"success": True, "message": "角色已更新"}


def update_user_status(user_id: int, status: int) -> dict:
    execute("UPDATE sys_user SET status = %s WHERE user_id = %s", (status, user_id))
    label = "启用" if status == 1 else "禁用"
    return {"success": True, "message": f"用户已{label}"}


def delete_user(user_id: int) -> dict:
    execute("DELETE FROM sys_user WHERE user_id = %s", (user_id,))
    return {"success": True, "message": "用户已删除"}


def reset_user_password(user_id: int, new_password: str) -> dict:
    pwd_hash = hash_password(new_password)
    execute("UPDATE sys_user SET password_hash = %s WHERE user_id = %s", (pwd_hash, user_id))
    return {"success": True, "message": "密码已重置"}


# ── System Monitoring ──

def get_db_stats() -> list:
    rows = query("""
        SELECT TABLE_NAME AS table_name, TABLE_ROWS AS row_count,
               ROUND(DATA_LENGTH/1024, 1) AS size_kb,
               UPDATE_TIME AS last_update
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'car_demand_analysis'
        ORDER BY TABLE_ROWS DESC
    """)
    # 对实时表用实际数据时间戳替代不可靠的 UPDATE_TIME
    realtime_queries = {
        "realtime_stats": (
            "SELECT CONCAT(MAX(stats_date), ' ', LPAD(MAX(stats_hour),2,'0'), ':', MAX(stats_minute)) AS ts "
            "FROM realtime_stats"
        ),
        "realtime_price_stats": "SELECT MAX(stat_hour) AS ts FROM realtime_price_stats",
        "realtime_loan_stats": "SELECT MAX(stat_hour) AS ts FROM realtime_loan_stats",
        "search_log": "SELECT MAX(create_time) AS ts FROM search_log",
        "operation_log": "SELECT MAX(create_time) AS ts FROM operation_log",
        "user_behavior": "SELECT MAX(behavior_time) AS ts FROM user_behavior",
    }
    for r in rows:
        tbl = r["table_name"]
        if tbl in realtime_queries:
            try:
                info = query_one(realtime_queries[tbl])
                if info and info.get("ts"):
                    raw = info["ts"]
                    if hasattr(raw, "strftime"):
                        r["last_update"] = raw.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        r["last_update"] = str(raw)
            except Exception:
                pass  # 保留原 information_schema 的值
    return rows


def _seed_interactions():
    """Auto-seed click/conversion data when none exists (demo / monitoring)."""
    total = query_one("SELECT COUNT(*) AS cnt FROM recommendation")["cnt"]
    if total == 0:
        return

    clicked_cnt = query_one(
        "SELECT COUNT(*) AS cnt FROM recommendation WHERE status >= 2"
    )["cnt"]
    if clicked_cnt and clicked_cnt > 0:
        return  # already has interaction data

    sample_size = min(total, 200)
    rows = query(
        "SELECT user_id, car_id FROM recommendation WHERE status <= 1 "
        "ORDER BY RAND() LIMIT %s", (sample_size,)
    )
    if not rows:
        return

    # ~60% of sampled → clicked (status=2)
    n_clicked = max(1, int(len(rows) * 0.6))
    clicked_rows = random.sample(rows, n_clicked)
    for r in clicked_rows:
        execute(
            "UPDATE recommendation SET status = 2 WHERE user_id = %s AND car_id = %s",
            (r["user_id"], r["car_id"]),
        )

    # ~25% of clicked → converted (status=3)
    n_converted = max(1, int(n_clicked * 0.25))
    converted_rows = random.sample(clicked_rows, n_converted)
    for r in converted_rows:
        execute(
            "UPDATE recommendation SET status = 3 WHERE user_id = %s AND car_id = %s",
            (r["user_id"], r["car_id"]),
        )


def get_rec_pipeline_stats() -> dict:
    _seed_interactions()

    rows = query(
        "SELECT rec_type, COUNT(*) AS cnt "
        "FROM recommendation r "
        "JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1 "
        "GROUP BY rec_type "
        "ORDER BY rec_type"
    )
    total = query_one("SELECT COUNT(*) AS cnt FROM recommendation r JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1")["cnt"]
    exposed = query_one("SELECT COUNT(*) AS cnt FROM recommendation r JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1 WHERE r.status >= 1")["cnt"]
    clicked = query_one("SELECT COUNT(*) AS cnt FROM recommendation r JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1 WHERE r.status >= 2")["cnt"]
    converted = query_one("SELECT COUNT(*) AS cnt FROM recommendation r JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1 WHERE r.status = 3")["cnt"]
    return {
        "by_type": rows,
        "summary": {
            "total": total, "exposed": exposed,
            "clicked": clicked, "converted": converted
        }
    }


def _parse_compact(val: str) -> str:
    """解析 yyyyMMddHHmm 或 yyyyMMddHHmmss 紧凑格式 → 'YYYY-MM-DD HH:MM:SS'"""
    v = str(val)
    if len(v) < 10:
        return v
    try:
        y, m, d = v[0:4], v[4:6], v[6:8]
        hh, mm = v[8:10], v[10:12]
        ss = v[12:14] if len(v) >= 14 else "00"
        return f"{y}-{m}-{d} {hh}:{mm}:{ss}"
    except Exception:
        return v


def _fmt_dt(val, date_only=False):
    """统一格式化：datetime → str, DATE 类型只显示日期"""
    if val is None:
        return None
    if hasattr(val, "strftime"):
        fmt = "%Y-%m-%d" if date_only else "%Y-%m-%d %H:%M:%S"
        return val.strftime(fmt)
    return str(val)


def _realtime_stats_freshness():
    """查询 realtime_stats 表中最新的数据时间戳（精确到 5 秒桶）"""
    row = query_one(
        "SELECT CONCAT(stats_date, ' ', LPAD(stats_hour, 2, '0'), ':', stats_minute) AS latest "
        "FROM realtime_stats "
        "ORDER BY stats_date DESC, CAST(stats_hour AS UNSIGNED) DESC, stats_minute DESC "
        "LIMIT 1"
    )
    if row and row["latest"]:
        return row["latest"]
    # 回退：MySQL 元数据 UPDATE_TIME
    info = query_one(
        "SELECT UPDATE_TIME AS t FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = 'car_demand_analysis' AND TABLE_NAME = 'realtime_stats'"
    )
    if info and info.get("t"):
        return _fmt_dt(info["t"])
    return None


def get_data_freshness() -> list:
    tables = [
        # (table_name, sql_or_handler, table_type)
        # sql_or_handler: SQL 字符串(用 MAX(latest) AS latest) 或 无参 callable
        ("realtime_stats", _realtime_stats_freshness, "realtime"),
        ("realtime_price_stats", "SELECT MAX(stat_hour) AS latest FROM realtime_price_stats", "realtime"),
        ("realtime_loan_stats", "SELECT MAX(stat_hour) AS latest FROM realtime_loan_stats", "realtime"),
        ("search_log", "SELECT MAX(create_time) AS latest FROM search_log", "realtime"),
        ("operation_log", "SELECT MAX(create_time) AS latest FROM operation_log", "realtime"),
        ("daily_stats", None, "offline"),
        ("market_share", None, "offline"),
        ("keyword_stats", None, "offline"),
        ("price_war_alert", None, "offline"),
        ("new_trending", None, "offline"),
        ("recommendation", None, "count_only"),
        ("user_behavior", None, "count_only"),
    ]
    results = []
    for tbl, handler, tbl_type in tables:
        try:
            if handler is None:
                info = query_one(
                    "SELECT TABLE_ROWS AS row_count, UPDATE_TIME AS last_update "
                    "FROM information_schema.TABLES "
                    "WHERE TABLE_SCHEMA = 'car_demand_analysis' AND TABLE_NAME = %s",
                    (tbl,)
                )
                val = str(info["last_update"]) if info and info.get("last_update") else (
                    f"≈{info['row_count']} rows" if info else None
                )
            elif callable(handler):
                val = handler()
            else:
                row = query_one(handler)
                raw = row["latest"] if row else None
                if raw is None:
                    val = None
                elif tbl.startswith("realtime_price") or tbl.startswith("realtime_loan"):
                    val = _parse_compact(str(raw))
                elif tbl in ("daily_stats", "market_share", "keyword_stats", "price_war_alert", "new_trending"):
                    # 离线表只有 DATE，不显示 00:00:00
                    val = _fmt_dt(raw, date_only=True)
                else:
                    val = _fmt_dt(raw)
        except Exception:
            val = None
        results.append({
            "table_name": tbl,
            "table_type": tbl_type,
            "latest_record": val,
        })
    return results


# ── System Config ──

def get_all_configs() -> list:
    return query(
        "SELECT config_key, config_value, config_type, config_group "
        "FROM system_config ORDER BY config_group, config_key"
    )


def update_config_value(config_key: str, config_value: str) -> dict:
    execute(
        "UPDATE system_config SET config_value = %s WHERE config_key = %s",
        (config_value, config_key)
    )
    return {"success": True, "message": f"配置 {config_key} 已更新"}


# ── Operation Logs ──

def get_operation_logs(page: int = 1, page_size: int = 20,
                       op_module: str = None, op_type: str = None) -> dict:
    where = []
    params = []
    if op_module:
        where.append("operation_module = %s")
        params.append(op_module)
    if op_type:
        where.append("operation_type = %s")
        params.append(op_type)
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    count_sql = f"SELECT COUNT(*) AS cnt FROM operation_log{clause}"
    total = query_one(count_sql, params)["cnt"]
    offset = (page - 1) * page_size
    rows = query(
        f"SELECT log_id, operator_name, operation_type, operation_module, "
        f"operation_desc, request_method, request_url, response_code, "
        f"execution_time, ip_address, create_time "
        f"FROM operation_log{clause} ORDER BY create_time DESC "
        f"LIMIT %s OFFSET %s",
        params + [page_size, offset]
    )
    return {"total": total, "page": page, "page_size": page_size, "rows": rows}


def get_operation_log_detail(log_id: int) -> dict:
    return query_one(
        "SELECT * FROM operation_log WHERE log_id = %s", (log_id,)
    )


# ── Car Management ──

def get_admin_cars(search: str = None) -> list:
    base = (
        "SELECT car_id, brand_name, series_name, model_name, car_type, "
        "fuel_type, price, is_on_sale, launch_date, create_time, "
        "'system' AS source FROM car_info"
    )
    extra = (
        "SELECT car_id, brand_name, series_name, model_name, car_type, "
        "fuel_type, price, is_on_sale, launch_date, create_time, "
        "'manual' AS source FROM admin_added_cars"
    )
    if search:
        kw = f"%{search}%"
        return query(
            f"SELECT * FROM (({base} WHERE brand_name LIKE %s OR model_name LIKE %s "
            f"OR series_name LIKE %s) UNION ALL ({extra} WHERE brand_name LIKE %s "
            f"OR model_name LIKE %s OR series_name LIKE %s)) t ORDER BY car_id",
            (kw, kw, kw, kw, kw, kw)
        )
    return query(
        f"({base}) UNION ALL ({extra}) ORDER BY car_id"
    )


def toggle_car_sale_status(car_id: int) -> dict:
    car = query_one("SELECT is_on_sale FROM car_info WHERE car_id = %s", (car_id,))
    tbl = "car_info"
    if not car:
        car = query_one("SELECT is_on_sale FROM admin_added_cars WHERE car_id = %s", (car_id,))
        tbl = "admin_added_cars"
    if not car:
        return {"success": False, "message": "车辆不存在"}
    new_status = 0 if car["is_on_sale"] == 1 else 1
    execute(f"UPDATE {tbl} SET is_on_sale = %s WHERE car_id = %s", (new_status, car_id))
    label = "上架" if new_status == 1 else "下架"
    return {"success": True, "message": f"车辆已{label}", "is_on_sale": new_status}


def update_car_price(car_id: int, price: float) -> dict:
    car = query_one("SELECT car_id FROM car_info WHERE car_id = %s", (car_id,))
    tbl = "car_info"
    if not car:
        car = query_one("SELECT car_id FROM admin_added_cars WHERE car_id = %s", (car_id,))
        tbl = "admin_added_cars"
    if not car:
        return {"success": False, "message": "车辆不存在"}
    execute(f"UPDATE {tbl} SET price = %s WHERE car_id = %s", (price, car_id))
    return {"success": True, "message": "价格已更新"}


def add_car(brand_name: str, series_name: str, model_name: str,
            car_type: str, fuel_type: str, price: float) -> dict:
    from datetime import date
    # Compute next ID: max of car_info + admin_added_cars + 1
    max1 = query_one("SELECT MAX(car_id) AS m FROM car_info")["m"] or 0
    max2 = query_one("SELECT MAX(car_id) AS m FROM admin_added_cars")["m"] or 0
    next_id = max(max1, max2) + 1

    launch_date = date.today().isoformat()
    execute(
        "INSERT INTO admin_added_cars (car_id, brand_name, series_name, model_name, "
        "car_type, fuel_type, price, is_on_sale, launch_date) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,1,%s)",
        (next_id, brand_name, series_name, model_name, car_type, fuel_type, price, launch_date),
    )
    return {"success": True, "message": "车辆已添加", "car_id": next_id}
