package com.car.analysis.common.model

case class UserBehavior(
    behavior_id: String,
    user_id: String,
    car_id: Int,
    behavior_type: String,
    behavior_time: String,
    brand_id: Int,
    brand_name: String,
    series_id: Int,
    car_type: String,
    fuel_type: String,
    price: Double,
    region_id: Int,
    session_id: String,
    search_keyword: String
)
