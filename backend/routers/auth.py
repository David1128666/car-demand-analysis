from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from services.auth_service import register_user, login_user, get_user_info, list_users
from auth_utils import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

class LoginBody(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=5, max_length=100)

class RegisterBody(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=5, max_length=100)
    nickname: str = Field(None, max_length=50)

@router.post("/register")
def register(body: RegisterBody):
    result = register_user(body.username, body.password, body.nickname)
    return {"code": 200 if result["success"] else 400, "data": result}

@router.post("/login")
def login(body: LoginBody):
    result = login_user(body.username, body.password)
    return {"code": 200 if result["success"] else 401, "data": result}

@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    info = get_user_info(user["user_id"])
    return {"code": 200, "data": info}

@router.get("/users")
def users(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        return {"code": 403, "message": "仅管理员可查看用户列表"}
    data = list_users()
    return {"code": 200, "data": data}