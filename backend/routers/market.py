from fastapi import APIRouter, Depends, Query
from services.market_service import (get_realtime_market_share, get_discount_tiers,
    get_brand_collect_rate, get_promotion_effect,
    get_brand_rank, get_market_share, get_keyword_cloud,
    get_price_war, get_price_reasons, get_fuel_trend, get_new_trending
)
from auth_utils import get_current_user

router = APIRouter(prefix="/api/v1/market", tags=["Market Insights"])

@router.get("/brand-rank")
def brand_rank(user: dict = Depends(get_current_user)):
    data = get_brand_rank()
    return {"code": 200, "data": data}

@router.get("/market-share")
def market_share(user: dict = Depends(get_current_user)):
    data = get_market_share()
    return {"code": 200, "data": data}

@router.get("/keyword-cloud")
def keyword_cloud(user: dict = Depends(get_current_user)):
    data = get_keyword_cloud()
    return {"code": 200, "data": data}

@router.get("/price-war")
def price_war(user: dict = Depends(get_current_user)):
    data = get_price_war()
    return {"code": 200, "data": data}

@router.get("/price-reasons")
def price_reasons(user: dict = Depends(get_current_user)):
    data = get_price_reasons()
    return {"code": 200, "data": data}

@router.get("/fuel-trend")
def fuel_trend(user: dict = Depends(get_current_user)):
    data = get_fuel_trend()
    return {"code": 200, "data": data}

@router.get("/new-trending")
def new_trending(user: dict = Depends(get_current_user)):
    data = get_new_trending()
    return {"code": 200, "data": data}
@router.get("/brand-collect-rate")
def brand_collect_rate(user: dict = Depends(get_current_user)):
    data = get_brand_collect_rate()
    return {"code": 200, "data": data}

@router.get("/promotion-effect")
def promotion_effect(user: dict = Depends(get_current_user)):
    data = get_promotion_effect()
    return {"code": 200, "data": data}

@router.get("/discount-tiers")
def discount_tiers(user: dict = Depends(get_current_user)):
    data = get_discount_tiers()
    return {"code": 200, "data": data}

@router.get("/realtime-market-share")
def realtime_market_share(brand_name: str = Query(None), user: dict = Depends(get_current_user)):
    data = get_realtime_market_share(brand_name)
    return {"code": 200, "data": data}