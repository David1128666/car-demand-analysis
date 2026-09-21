package com.car.analysis.common.model

case class CarPriceQuote(
    quote_id: String,
    car_id: Int,
    brand_id: Int,
    brand_name: String,
    series_id: Int,
    car_type: String,
    original_price: Double,
    quoted_price: Double,
    discount_rate: Double,
    price_change_reason: String,
    region_id: Int,
    dealer_id: String,
    quote_time: String,
    validity_period: Int,
    promotion_info: String
)
