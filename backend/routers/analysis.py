from fastapi import APIRouter, Depends, Query
from services.analysis_service import (
    get_car_type_preference, get_brand_consult_rate, get_loan_approval_rate,
    get_daily_trend, get_brand_popularity, get_user_behavior_stats,
    get_recommendation_stats, get_user_profile
)
from auth_utils import get_current_user

router = APIRouter(prefix="/api/v1/analysis", tags=["Analysis"])

@router.get("/trend")
def daily_trend(user: dict = Depends(get_current_user)):
    data = get_daily_trend()
    return {"code": 200, "data": data}

@router.get("/brand-popularity")
def brand_popularity(user: dict = Depends(get_current_user)):
    data = get_brand_popularity()
    return {"code": 200, "data": data}

@router.get("/user-behavior")
def user_behavior(user: dict = Depends(get_current_user)):
    data = get_user_behavior_stats()
    return {"code": 200, "data": data}

@router.get("/rec-stats")
def rec_stats(user: dict = Depends(get_current_user)):
    data = get_recommendation_stats()
    return {"code": 200, "data": data}

@router.get("/user-profile")
def user_profile(user_id: str = Query(None), user: dict = Depends(get_current_user)):
    data = get_user_profile(user_id)
    return {"code": 200, "data": data}
@router.get("/car-type-preference")
def car_type_preference(user: dict = Depends(get_current_user)):
    data = get_car_type_preference()
    return {"code": 200, "data": data}

@router.get("/brand-consult-rate")
def brand_consult_rate(user: dict = Depends(get_current_user)):
    data = get_brand_consult_rate()
    return {"code": 200, "data": data}

@router.get("/loan-approval-rate")
def loan_approval_rate(user: dict = Depends(get_current_user)):
    data = get_loan_approval_rate()
    return {"code": 200, "data": data}
