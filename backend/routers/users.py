"""用户相关路由"""

from fastapi import APIRouter, HTTPException, Depends, Header
from models import UserRegister, UserLogin, UserResponse, TokenResponse
from database import Database
from auth import create_access_token, verify_token

router = APIRouter(prefix="/api/auth", tags=["认证"])


def get_current_user(authorization: str = Header(None)):
    """从请求头解析当前用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")
    return payload


def get_admin_user(current_user: dict = Depends(get_current_user)):
    """验证管理员权限"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


@router.post("/register", response_model=dict)
def register(user: UserRegister):
    """用户注册"""
    success, message = Database.register(
        username=user.username,
        password=user.password,
        role=user.role,
        name=user.name,
        phone=user.phone,
        student_id=user.student_id,
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@router.post("/login")
def login(user: UserLogin):
    """用户登录，返回 JWT 令牌"""
    user_data = Database.login(user.username, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({
        "sub": user_data["username"],
        "role": user_data["role"],
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_data,
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前登录用户信息"""
    username = current_user.get("sub")
    user = Database.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


# ==================== 用户管理（管理员） ====================

admin_router = APIRouter(prefix="/api/users", tags=["用户管理"])


@admin_router.get("")
def list_users(_=Depends(get_admin_user)):
    """获取所有用户（管理员）"""
    return Database.get_all_users()


@admin_router.get("/{username}")
def get_user(username: str, _=Depends(get_current_user)):
    """获取指定用户信息"""
    user = Database.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
