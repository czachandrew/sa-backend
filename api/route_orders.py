from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from .auth import get_current_user
from sqlalchemy.orm import Session
from database import get_db, CreateOrderItem
from models import User, Order, OrderItem
from typing import List
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import Item

from mail import send_email

router = APIRouter()


class UserBase(BaseModel):
    email: str


class OrderItemBase(BaseModel):
    id: int
    order_id: Optional[int] = None
    inventory_id: Optional[int] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    price: Optional[float] = None
    product: Item


class OrderBase(BaseModel):
    id: int
    user_id: int
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    total: Optional[float] = None
    items: List[OrderItemBase] = []
    user: UserBase


@router.post("/create/")
async def create_order(
    order_items: List[CreateOrderItem],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print("requesting user is ")
    print(user.email)
    newOrder = Order(
        user_id=user.id, status="requested", total=0, created_at="now", updated_at="now"
    )
    db.add(newOrder)
    db.commit()
    db.refresh(newOrder)
    print("new order id is ")
    print(newOrder.id)
    total = 0
    for order_item in order_items:
        print("here is the item as we loop through")
        print(order_item.item)
        new_order_item = OrderItem(
            order_id=newOrder.id,
            inventory_id=order_item.item.id,
            quantity=order_item.quantity,
            status="pending",
            price=order_item.item.price,
        )
        total += order_item.item.price * order_item.quantity
        db.add(new_order_item)
        db.commit()
        db.refresh(new_order_item)

    newOrder.total = total
    db.commit()
    print(user)
    send_email("andrewczachowski@me.com", "New Order Test", order_items, newOrder)
    return {"message": "Order endpoint accessed"}


@router.get("/list/open/", response_model=List[OrderBase])
async def list_orders(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    orders = db.query(Order).filter(Order.status != "closed").all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    print(orders)
    return orders


# Now, use these models in your endpoint:
@router.get("/user/", response_model=List[OrderBase])  # list of Order submodels
async def get_orders_by_user(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user.id
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    print(orders)
    return orders


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


@router.get("/cancel/{order_id}/")
async def cancel_order(
    db: Session = Depends(get_db),
    order_id: int = None,
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = "cancelled"
    db.commit()
    return order


@router.get("/delete/{order_id}/")
async def delete_order(
    db: Session = Depends(get_db),
    order_id: int = None,
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return order


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
