"""Pydantic 数据模型（请求/响应校验）"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


# ==================== 用户模型 ====================

class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=4, max_length=100)
    role: Literal["requester", "delivery"]
    name: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=5, max_length=20)
    student_id: Optional[str] = ""


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    role: str
    name: str
    phone: str
    student_id: Optional[str] = ""
    avatar: Optional[str] = ""
    rating: float = 0.0
    completed: int = 0
    balance: float = 0.0
    created_at: Optional[str] = None


# ==================== 订单模型 ====================

class OrderCreate(BaseModel):
    type: str = Field(description="订单类型：快递代取/外卖代送/文件代送/其他")
    details: str = Field(max_length=500)
    pickup: str = Field(max_length=200)
    dropoff: str = Field(max_length=200)
    reward: float = Field(gt=0)
    note: Optional[str] = ""


class OrderResponse(BaseModel):
    id: str
    requester: str
    type: str
    details: str
    pickup: str
    dropoff: str
    reward: float
    note: Optional[str] = ""
    status: str
    delivery_person: Optional[str] = None
    created_at: Optional[str] = None
    accepted_at: Optional[str] = None
    completed_at: Optional[str] = None


# ==================== 评价模型 ====================

class ReviewCreate(BaseModel):
    order_id: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = ""


class ReviewResponse(BaseModel):
    order_id: str
    requester: str
    delivery_person: str
    rating: int
    comment: Optional[str] = ""


class ProfileUpdate(BaseModel):
    """更新个人资料"""
    name: str = Field(min_length=1, max_length=50, description="用户昵称")


# ==================== 通用响应 ====================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class StatsResponse(BaseModel):
    total_users: int
    total_orders: int
    active_orders: int
    completed_orders: int
    pending_orders: int
    total_requesters: int
    total_delivery: int
