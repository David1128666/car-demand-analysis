package com.car.analysis.common.model

case class CarSearch(
    search_id: String,
    user_id: String,
    search_keyword: String,
    search_time: String,
    region_id: Int,
    result_count: Int,
    click_position: Int
)
