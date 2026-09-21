package com.car.analysis.common.model

case class CarLoanInquiry(
    loan_id: String,
    user_id: String,
    car_id: Int,
    brand_id: Int,
    car_type: String,
    loan_type: String,
    car_price: Double,
    down_payment: Double,
    loan_amount: Double,
    loan_term: Int,
    interest_rate: Double,
    monthly_payment: Double,
    region_id: Int,
    credit_score: Int,
    inquiry_time: String,
    loan_status: String,
    has_insurance: Boolean,
    preferred_bank: String
)
