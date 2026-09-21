from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from services.recommendation_service import (
    get_home_recommendations, get_similar_cars, get_hot_recommendations,
    get_recommendation_users, mark_clicked, mark_converted,
    get_rec_summary, get_top_recommended_cars
)
from auth_utils import get_current_user
from database import get_system_config_int


class RecAction(BaseModel):
    user_id: str
    car_id: int

router = APIRouter(prefix="/api/v1/rec", tags=["Recommendation"])

@router.get("/home")
def home_rec(user_id: str = Query(...), limit: int = Query(None),
             user: dict = Depends(get_current_user)):
    if limit is None:
        limit = get_system_config_int("sys.recommend.home.size", 20)
    data = get_home_recommendations(user_id, limit)
    return {"code": 200, "data": data}

@router.get("/similar")
def similar_rec(car_id: int = Query(...), limit: int = Query(None),
                user: dict = Depends(get_current_user)):
    if limit is None:
        limit = get_system_config_int("sys.recommend.similar.size", 10)
    data = get_similar_cars(car_id, limit)
    return {"code": 200, "data": data}

@router.get("/hot")
def hot_rec(limit: int = Query(None), user: dict = Depends(get_current_user)):
    if limit is None:
        limit = get_system_config_int("sys.recommend.hot.size", 50)
    data = get_hot_recommendations(limit)
    return {"code": 200, "data": data}


@router.get("/users")
def rec_users(user: dict = Depends(get_current_user)):
    data = get_recommendation_users()
    return {"code": 200, "data": [r["user_id"] for r in data]}


@router.post("/click")
def rec_click(body: RecAction, user: dict = Depends(get_current_user)):
    mark_clicked(body.user_id, body.car_id)
    return {"code": 200, "message": "ok"}


@router.post("/convert")
def rec_convert(body: RecAction, user: dict = Depends(get_current_user)):
    mark_converted(body.user_id, body.car_id)
    return {"code": 200, "message": "ok"}


@router.get("/summary")
def rec_summary(user: dict = Depends(get_current_user)):
    data = get_rec_summary()
    return {"code": 200, "data": data}


@router.get("/top-cars")
def rec_top_cars(limit: int = Query(10), user: dict = Depends(get_current_user)):
    data = get_top_recommended_cars(limit)
    return {"code": 200, "data": data}