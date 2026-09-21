from database import query, query_one, execute
from auth_utils import hash_password, verify_password, create_token

def register_user(username: str, password: str, nickname: str = None, role: str = "user") -> dict:
    existing = query_one("SELECT user_id FROM sys_user WHERE username = %s", (username,))
    if existing:
        return {"success": False, "message": "用户名已存在"}

    pwd_hash = hash_password(password)
    user_id = execute(
        "INSERT INTO sys_user (username, password_hash, nickname, role) VALUES (%s,%s,%s,%s)",
        (username, pwd_hash, nickname or username, role)
    )
    return {"success": True, "message": "注册成功", "user_id": user_id}

def login_user(username: str, password: str) -> dict:
    user = query_one(
        "SELECT user_id, username, password_hash, nickname, role, status FROM sys_user WHERE username = %s",
        (username,)
    )
    if not user:
        return {"success": False, "message": "用户名或密码错误"}

    if user["status"] != 1:
        return {"success": False, "message": "账号已被禁用"}

    if not verify_password(password, user["password_hash"]):
        return {"success": False, "message": "用户名或密码错误"}

    execute("UPDATE sys_user SET last_login = NOW() WHERE user_id = %s", (user["user_id"],))

    token = create_token(user["user_id"], user["username"], user["role"])
    return {
        "success": True,
        "message": "登录成功",
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "nickname": user["nickname"],
            "role": user["role"]
        }
    }

def get_user_info(user_id: int) -> dict:
    user = query_one(
        "SELECT user_id, username, nickname, role, email, phone, status, last_login, create_time FROM sys_user WHERE user_id = %s",
        (user_id,)
    )
    if not user:
        return None
    # Convert datetime to string
    for k in ("last_login", "create_time"):
        if user.get(k):
            user[k] = user[k].isoformat()
    return user

def list_users() -> list:
    return query(
        "SELECT user_id, username, nickname, role, email, phone, status, last_login, create_time FROM sys_user ORDER BY create_time"
    )