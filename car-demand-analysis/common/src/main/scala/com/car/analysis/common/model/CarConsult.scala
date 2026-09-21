package com.car.analysis.common.model

case class CarConsult(
    consult_id: String,
    user_id: String,
    car_id: Int,
    consult_time: String,
    consult_type: String,
    region_id: Int,
    has_phone: Boolean,
    followup_status: String
)
