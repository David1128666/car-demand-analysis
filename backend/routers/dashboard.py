from fastapi import APIRouter, Depends, Query
from services.dashboard_service import (
    get_overview, get_realtime_stats, get_price_stats,
    get_loan_stats, get_finance_summary
)
from auth_utils import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

@router.get("/overview")
def overview(user: dict = Depends(get_current_user)):
    data = get_overview()
    return {"code": 200, "data": data}

@router.get("/realtime-stats")
def realtime_stats(user: dict = Depends(get_current_user)):
    data = get_realtime_stats()
    return {"code": 200, "data": data}

@router.get("/price-stats")
def price_stats(
    brand_id: int = Query(None), car_type: str = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
    user: dict = Depends(get_current_user)):
    data = get_price_stats(brand_id, car_type, start_date, end_date)
    return {"code": 200, "data": data}

@router.get("/loan-stats")
def loan_stats(
    brand_id: int = Query(None), car_type: str = Query(None),
    loan_type: str = Query(None), start_date: str = Query(None),
    end_date: str = Query(None),
    user: dict = Depends(get_current_user)):
    data = get_loan_stats(brand_id, car_type, loan_type, start_date, end_date)
    return {"code": 200, "data": data}

@router.get("/finance-summary")
def finance_summary(user: dict = Depends(get_current_user)):
    data = get_finance_summary()
    return {"code": 200, "data": data}