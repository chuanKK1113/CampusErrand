"""评价相关路由"""

from fastapi import APIRouter, HTTPException, Depends
from models import ReviewCreate, ReviewResponse
from database import Database
from routers.users import get_current_user

router = APIRouter(prefix="/api/reviews", tags=["评价"])


@router.post("")
def add_review(review: ReviewCreate, current_user: dict = Depends(get_current_user)):
    """提交评价"""
    username = current_user.get("sub")

    # 验证订单存在
    order = Database.get_order(review.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 验证是订单的需求方
    if order["requester"] != username:
        raise HTTPException(status_code=403, detail="只有订单发布者可以评价")

    # 验证订单已完成
    if order["status"] != "已完成":
        raise HTTPException(status_code=400, detail="只能对已完成订单进行评价")

    # 验证配送员存在
    if not order.get("delivery_person"):
        raise HTTPException(status_code=400, detail="该订单没有配送员")

    success, message = Database.add_review(
        order_id=review.order_id,
        requester=username,
        delivery_person=order["delivery_person"],
        rating=review.rating,
        comment=review.comment or "",
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@router.get("/check/{order_id}")
def check_review(order_id: str):
    """检查订单是否已被评价"""
    exists = Database.review_exists(order_id)
    return {"exists": exists}


@router.get("/mine")
def get_my_reviews(current_user: dict = Depends(get_current_user)):
    """获取当前用户的评价（需求方）"""
    username = current_user.get("sub")
    return Database.get_reviews_by_requester(username)


@router.get("/delivery/{username}")
def get_delivery_reviews(username: str, current_user: dict = Depends(get_current_user)):
    """获取配送员的评价"""
    return Database.get_reviews_by_delivery(username)
