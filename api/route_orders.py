from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from .auth import get_current_user
from sqlalchemy.orm import Session
from database import get_db, CreateOrderItem
from models import User, Order, OrderItem
from typing import List

router = APIRouter()


@router.post("/create/")
async def create_order(
    order_items: List[CreateOrderItem],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for order_item in order_items:
        print(order_item)
    print(user)
    return {"message": "Order endpoint accessed"}


@router.post("/add_item/{order_id}")
async def add_item_to_order(
    order_item: CreateOrderItem,
    order_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    new_order_item = OrderItem(
        order_id=order.id,
        inventory_id=order_item.item.id,
        quantity=order_item.quantity,
        status="pending",
        price=order_item.item.price,
    )
    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)
    return new_order_item


@router.post("/cart/")
async def create_cart(
    order_items: List[CreateOrderItem],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # creat a new order
    order = Order(user_id=user.id, status="cart")
    db.add(order)
    db.commit()
    db.refresh(order)
    # add order items to the order
    created_items = []
    for order_item in order_items:
        print(order_item)
        new_order_item = OrderItem(
            order_id=order.id,
            inventory_id=order_item.item.id,
            quantity=order_item.quantity,
            status="pending",
            price=order_item.item.price,
        )
        db.add(new_order_item)
        db.commit()
        db.refresh(new_order_item)
        created_items.append(new_order_item)
    print(created_items)
    print(user)
    return {"cart": order, "items": created_items}
