from fastapi import APIRouter, Depends, Query
from services.car_service import get_car_list, get_car_detail, get_brands
from auth_utils import get_current_user

router = APIRouter(prefix="/api/v1/cars", tags=["Cars"])

@router.get("")
def car_list(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100),
    brand_id: int = Query(None), car_type: str = Query(None),
    fuel_type: str = Query(None), price_min: float = Query(None),
    price_max: float = Query(None),
    user: dict = Depends(get_current_user)):
    data = get_car_list(page, size, brand_id, car_type, fuel_type, price_min, price_max)
    return {"code": 200, "data": data}

@router.get("/{car_id}")
def car_detail(car_id: int, user: dict = Depends(get_current_user)):
    data = get_car_detail(car_id)
    if not data:
        return {"code": 404, "message": "Car not found"}
    return {"code": 200, "data": data}

@router.get("/meta/brands")
def brands(user: dict = Depends(get_current_user)):
    data = get_brands()
    return {"code": 200, "data": data}