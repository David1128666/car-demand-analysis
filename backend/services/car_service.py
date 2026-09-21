from database import query, query_one

def get_car_list(page: int = 1, size: int = 10, brand_id: int = None,
                 car_type: str = None, fuel_type: str = None,
                 price_min: float = None, price_max: float = None):
    # Filters that apply to both v_car_full_info and admin_added_cars
    common = []
    params_all = []
    if car_type:
        common.append("car_type = %s")
        params_all.append(car_type)
    if fuel_type:
        common.append("fuel_type = %s")
        params_all.append(fuel_type)
    if price_min is not None:
        common.append("price >= %s")
        params_all.append(price_min)
    if price_max is not None:
        common.append("price <= %s")
        params_all.append(price_max)

    common_where = (" AND ".join(common)) if common else "1=1"

    # v_car_full_info part (may have extra brand_id filter)
    info_conds = list(common)
    info_params = list(params_all)
    if brand_id:
        info_conds.append("brand_id = %s")
        info_params.append(brand_id)
    info_where = (" AND ".join(info_conds)) if info_conds else "1=1"

    include_admin = (brand_id is None)

    if include_admin:
        count_sql = (
            "SELECT COUNT(*) AS total FROM ("
            f"SELECT car_id FROM v_car_full_info WHERE {info_where} "
            "UNION ALL "
            f"SELECT car_id FROM admin_added_cars WHERE {common_where}"
            ") t"
        )
        count_params = info_params + params_all
    else:
        count_sql = f"SELECT COUNT(*) AS total FROM v_car_full_info WHERE {info_where}"
        count_params = info_params

    total = query_one(count_sql, count_params)["total"]
    offset = (page - 1) * size

    info_cols = (
        "car_id, brand_id, brand_name, series_id, series_name, "
        "model_name, car_type, fuel_type, price, launch_date, country"
    )
    admin_cols = (
        "car_id, NULL AS brand_id, brand_name, NULL AS series_id, series_name, "
        "model_name, car_type, fuel_type, price, launch_date, NULL AS country"
    )

    if include_admin:
        list_sql = (
            f"SELECT {info_cols} FROM v_car_full_info WHERE {info_where} "
            "UNION ALL "
            f"SELECT {admin_cols} FROM admin_added_cars WHERE {common_where} "
            "ORDER BY car_id LIMIT %s OFFSET %s"
        )
        list_params = info_params + params_all + [size, offset]
    else:
        list_sql = (
            f"SELECT {info_cols} FROM v_car_full_info WHERE {info_where} "
            "ORDER BY car_id LIMIT %s OFFSET %s"
        )
        list_params = info_params + [size, offset]

    rows = query(list_sql, list_params)
    return {"total": total, "page": page, "size": size, "list": rows}

def get_car_detail(car_id: int):
    car = query_one("SELECT * FROM v_car_full_info WHERE car_id = %s", (car_id,))
    if not car:
        car = query_one("SELECT *, NULL AS brand_id, NULL AS series_id, NULL AS country "
                        "FROM admin_added_cars WHERE car_id = %s", (car_id,))
    if not car:
        return None

    stats_sql = """
        SELECT COUNT(*) AS total_views,
               COUNT(DISTINCT user_id) AS unique_users
        FROM user_behavior WHERE car_id = %s
    """
    stats = query_one(stats_sql, (car_id,))
    car["total_views"] = stats["total_views"] if stats else 0
    car["unique_users"] = stats["unique_users"] if stats else 0

    return car

def get_brands():
    sql = """
        SELECT DISTINCT brand_id, brand_name FROM v_car_full_info
        WHERE brand_id IS NOT NULL
        ORDER BY brand_name
    """
    return query(sql)