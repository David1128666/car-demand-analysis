from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from services.admin_service import (
    list_users, create_user, update_user_role, update_user_status,
    delete_user, reset_user_password, get_db_stats, get_rec_pipeline_stats,
    get_data_freshness, get_all_configs, update_config_value,
    get_operation_logs, get_operation_log_detail,
    get_admin_cars, toggle_car_sale_status, update_car_price, add_car
)
from auth_utils import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


def require_admin(user: dict):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")


# ── Pydantic models ──

class CreateUserBody(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=5, max_length=100)
    nickname: str = Field(None, max_length=50)
    role: str = Field("user")
    email: str = Field(None, max_length=100)
    phone: str = Field(None, max_length=20)


class UpdateRoleBody(BaseModel):
    role: str


class UpdateStatusBody(BaseModel):
    status: int


class ResetPasswordBody(BaseModel):
    password: str = Field(..., min_length=5, max_length=100)


class UpdateConfigBody(BaseModel):
    config_value: str


class UpdatePriceBody(BaseModel):
    price: float


class AddCarBody(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=100)
    series_name: str = Field(..., min_length=1, max_length=100)
    model_name: str = Field(..., min_length=1, max_length=200)
    car_type: str = Field(..., min_length=1, max_length=50)
    fuel_type: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)


# ── User Management ──

@router.get("/users")
def admin_list_users(user: dict = Depends(get_current_user)):
    require_admin(user)
    return {"code": 200, "data": list_users()}


@router.post("/users")
def admin_create_user(body: CreateUserBody, user: dict = Depends(get_current_user)):
    require_admin(user)
    result = create_user(body.username, body.password, body.nickname,
                         body.role, body.email, body.phone)
    return {"code": 200 if result["success"] else 400, "data": result}


@router.put("/users/{user_id}/role")
def admin_update_role(user_id: int, body: UpdateRoleBody,
                      user: dict = Depends(get_current_user)):
    require_admin(user)
    result = update_user_role(user_id, body.role)
    return {"code": 200, "data": result}


@router.put("/users/{user_id}/status")
def admin_update_status(user_id: int, body: UpdateStatusBody,
                        user: dict = Depends(get_current_user)):
    require_admin(user)
    result = update_user_status(user_id, body.status)
    return {"code": 200, "data": result}


@router.delete("/users/{user_id}")
def admin_delete_user(user_id: int, user: dict = Depends(get_current_user)):
    require_admin(user)
    if user_id == user["user_id"]:
        return {"code": 400, "message": "不能删除自己"}
    result = delete_user(user_id)
    return {"code": 200, "data": result}


@router.put("/users/{user_id}/password")
def admin_reset_password(user_id: int, body: ResetPasswordBody,
                         user: dict = Depends(get_current_user)):
    require_admin(user)
    result = reset_user_password(user_id, body.password)
    return {"code": 200, "data": result}


# ── System Monitoring ──

@router.get("/db-stats")
def admin_db_stats(user: dict = Depends(get_current_user)):
    require_admin(user)
    return {"code": 200, "data": get_db_stats()}


@router.get("/rec-pipeline")
def admin_rec_pipeline(user: dict = Depends(get_current_user)):
    require_admin(user)
    return {"code": 200, "data": get_rec_pipeline_stats()}


@router.get("/data-freshness")
def admin_data_freshness(user: dict = Depends(get_current_user)):
    require_admin(user)
    return {"code": 200, "data": get_data_freshness()}


# ── System Config ──

@router.get("/config")
def admin_get_config(user: dict = Depends(get_current_user)):
    require_admin(user)
    return {"code": 200, "data": get_all_configs()}


@router.put("/config/{config_key}")
def admin_update_config(config_key: str, body: UpdateConfigBody,
                        user: dict = Depends(get_current_user)):
    require_admin(user)
    result = update_config_value(config_key, body.config_value)
    return {"code": 200, "data": result}


# ── Operation Logs ──

@router.get("/operation-logs")
def admin_operation_logs(page: int = Query(1), page_size: int = Query(20),
                         op_module: str = Query(None), op_type: str = Query(None),
                         user: dict = Depends(get_current_user)):
    require_admin(user)
    return {"code": 200, "data": get_operation_logs(page, page_size, op_module, op_type)}


@router.get("/operation-logs/{log_id}")
def admin_operation_log_detail(log_id: int, user: dict = Depends(get_current_user)):
    require_admin(user)
    data = get_operation_log_detail(log_id)
    return {"code": 200, "data": data}


# ── Car Management ──

@router.get("/cars")
def admin_cars(search: str = Query(None), user: dict = Depends(get_current_user)):
    require_admin(user)
    return {"code": 200, "data": get_admin_cars(search)}


@router.put("/cars/{car_id}/toggle-sale")
def admin_toggle_car_sale(car_id: int, user: dict = Depends(get_current_user)):
    require_admin(user)
    result = toggle_car_sale_status(car_id)
    return {"code": 200, "data": result}


@router.put("/cars/{car_id}/price")
def admin_update_car_price(car_id: int, body: UpdatePriceBody,
                           user: dict = Depends(get_current_user)):
    require_admin(user)
    result = update_car_price(car_id, body.price)
    return {"code": 200, "data": result}


@router.post("/cars")
def admin_add_car(body: AddCarBody, user: dict = Depends(get_current_user)):
    require_admin(user)
    result = add_car(body.brand_name, body.series_name, body.model_name,
                     body.car_type, body.fuel_type, body.price)
    return {"code": 200, "data": result}
