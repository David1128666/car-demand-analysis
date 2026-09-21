from database import query, query_one, execute


def get_home_recommendations(user_id: str, limit: int = 10):
    sql = """
        SELECT r.user_id, r.car_id, r.rec_type, r.rec_position, r.score,
               r.reason, r.reason_type, r.status,
               c.brand_name, c.series_name, c.model_name, c.car_type,
               c.fuel_type, c.price, c.launch_date
        FROM recommendation r
        LEFT JOIN car_info c ON r.car_id = c.car_id
        WHERE r.user_id = %s
        ORDER BY r.rec_position
        LIMIT %s
    """
    rows = query(sql, (user_id, limit))

    if rows:
        rec_ids = [row["car_id"] for row in rows]
        # Mark as exposed (status=1) if not already
        execute(
            """UPDATE recommendation SET status = 1
               WHERE user_id = %s AND car_id IN ({}) AND status = 0""".format(
                ",".join(["%s"] * len(rec_ids))),
            (user_id, *rec_ids),
        )

    return rows


def get_hot_recommendations(limit: int = 10):
    sql = """
        SELECT c.car_id, c.brand_name, c.series_name, c.model_name,
               c.car_type, c.fuel_type, c.price, c.launch_date,
               COUNT(ub.behavior_id) AS view_count,
               COUNT(DISTINCT ub.user_id) AS unique_users
        FROM car_info c
        LEFT JOIN user_behavior ub ON c.car_id = ub.car_id
        WHERE c.is_on_sale = 1
        GROUP BY c.car_id
        ORDER BY view_count DESC
        LIMIT %s
    """
    return query(sql, (limit,))


def get_similar_cars(car_id: int, limit: int = 5):
    sql = """
        SELECT c2.car_id, c2.brand_name, c2.series_name, c2.model_name,
               c2.car_type, c2.fuel_type, c2.price,
               COUNT(DISTINCT ub.user_id) AS common_users
        FROM user_behavior ub
        JOIN car_info c1 ON ub.car_id = c1.car_id
        JOIN car_info c2 ON c1.brand_id = c2.brand_id OR c1.car_type = c2.car_type
        WHERE ub.car_id = %s AND c2.car_id != %s AND c2.is_on_sale = 1
        GROUP BY c2.car_id
        ORDER BY common_users DESC, c2.price
        LIMIT %s
    """
    return query(sql, (car_id, car_id, limit))


def get_recommendation_users():
    sql = "SELECT DISTINCT user_id FROM recommendation ORDER BY user_id LIMIT 100"
    return query(sql)


def mark_clicked(user_id: str, car_id: int):
    """Mark a recommendation as clicked (status=2)."""
    execute(
        """UPDATE recommendation SET status = 2
         WHERE user_id = %s AND car_id = %s AND status < 2""",
        (user_id, car_id),
    )


def mark_converted(user_id: str, car_id: int):
    """Mark a recommendation as converted (status=3)."""
    execute(
        """UPDATE recommendation SET status = 3
         WHERE user_id = %s AND car_id = %s AND status < 3""",
        (user_id, car_id),
    )


def get_rec_summary() -> dict:
    """Admin: overview stats for the recommendation engine."""
    total = query_one(
        "SELECT COUNT(*) AS cnt FROM recommendation r "
        "JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1"
    )["cnt"]
    user_count = query_one(
        "SELECT COUNT(DISTINCT user_id) AS cnt FROM recommendation"
    )["cnt"]
    by_type = query(
        "SELECT rec_type, COUNT(*) AS cnt FROM recommendation r "
        "JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1 "
        "GROUP BY rec_type"
    )
    by_status = query(
        "SELECT r.status, COUNT(*) AS cnt FROM recommendation r "
        "JOIN car_info c ON r.car_id = c.car_id AND c.is_on_sale = 1 "
        "GROUP BY r.status"
    )
    return {"total": total, "user_count": user_count, "by_type": by_type, "by_status": by_status}


def get_top_recommended_cars(limit: int = 10) -> list:
    """Admin: most frequently recommended cars across all users."""
    return query(
        """SELECT c.car_id, c.brand_name, c.model_name, c.car_type,
                  c.price, COUNT(*) AS rec_count,
                  COUNT(DISTINCT r.user_id) AS user_count
           FROM recommendation r
           JOIN car_info c ON r.car_id = c.car_id
           WHERE c.is_on_sale = 1
           GROUP BY c.car_id
           ORDER BY rec_count DESC
           LIMIT %s""",
        (limit,),
    )
