"""订单相关路由"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from models import OrderCreate, OrderResponse
from database import Database
from routers.users import get_current_user, get_admin_user

router = APIRouter(prefix="/api/orders", tags=["订单"])


@router.post("")
def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    """创建新订单"""
    username = current_user.get("sub")
    if current_user.get("role") != "requester":
        raise HTTPException(status_code=403, detail="只有需求方可以发布订单")

    success, message, order_id = Database.create_order(
        requester=username,
        order_type=order.type,
        details=order.details,
        pickup=order.pickup,
        dropoff=order.dropoff,
        reward=order.reward,
        note=order.note or "",
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message, "order_id": order_id}


@router.get("")
def list_orders(
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    获取订单列表
    - 需求方：查看自己的订单
    - 配送员：查看可接单列表或自己的配送订单
    """
    username = current_user.get("sub")
    user_role = current_user.get("role")

    if user_role == "requester":
        orders = Database.get_orders_by_user(username, status)
    elif user_role == "delivery":
        if role == "mine":
            orders = Database.get_orders_by_delivery(username, status)
        else:
            if status:
                all_available = Database.get_available_orders()
                orders = [o for o in all_available if o["status"] == status]
            else:
                orders = Database.get_available_orders()
    else:
        orders = Database.get_all_orders()

    return orders


@router.get("/available")
def get_available_orders(current_user: dict = Depends(get_current_user)):
    """获取所有待接单订单（配送员用）"""
    return Database.get_available_orders()


@router.get("/mine")
def get_my_orders(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """获取当前用户的需求订单（需求方用）"""
    username = current_user.get("sub")
    return Database.get_orders_by_user(username, status)


@router.get("/delivery")
def get_my_deliveries(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """获取当前配送员的配送订单"""
    username = current_user.get("sub")
    if current_user.get("role") != "delivery":
        raise HTTPException(status_code=403, detail="只有配送员可以查看配送列表")
    return Database.get_orders_by_delivery(username, status)


@router.get("/{order_id}")
def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """获取订单详情"""
    order = Database.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.put("/{order_id}/accept")
def accept_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """配送员接单"""
    if current_user.get("role") != "delivery":
        raise HTTPException(status_code=403, detail="只有配送员可以接单")

    username = current_user.get("sub")
    success, message = Database.accept_order(order_id, username)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@router.put("/{order_id}/complete")
def complete_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """确认送达"""
    if current_user.get("role") != "delivery":
        raise HTTPException(status_code=403, detail="只有配送员可以确认送达")

    success, message = Database.complete_order(order_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@router.put("/{order_id}/cancel")
def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """取消订单"""
    order = Database.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    username = current_user.get("sub")
    if order["requester"] != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权取消此订单")

    success, message = Database.cancel_order(order_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


# ==================== 管理员订单接口 ====================

admin_router = APIRouter(prefix="/api/admin/orders", tags=["管理员-订单"])


@admin_router.get("")
def admin_list_orders(_=Depends(get_admin_user)):
    """管理员获取所有订单"""
    return Database.get_all_orders()
