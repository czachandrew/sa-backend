from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Form,
    UploadFile,
    File,
    Request,
)
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
import stripe
import json

from mail import send_email

router = APIRouter()


class UserBase(BaseModel):
    email: str


class SuccessResponse(BaseModel):
    success: bool


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
    payment_link: Optional[str] = None
    total: Optional[float] = None
    items: List[OrderItemBase] = []
    user: UserBase


# The library needs to be configured with your account's secret key.
# Ensure the key is kept out of any version control system you might be using.
stripe.api_key = "sk_test_51H5GbkLXAFRviTEvEoyQiHYkHGFjF2FUIS3Kv2C3XzoOUoRCTjyF3fI4nBiPmlUwIRYaamAbwMDouXmXbSRSOLZT00jYE9SJ4T"

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = (
    "whsec_e372be1f3db91ba5041ea3c67956e9b282cc805f17492f4af18466dafe929428"
)


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


@router.post("/update/{order_id}/", response_model=OrderBase)
async def update_order(
    order_id: int,
    order: OrderBase,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.status = order.status
    db_order.payment_link = order.payment_link
    if order.payment_link is not None:
        db_order.status = "awaiting payment"
    db.commit()
    db.refresh(db_order)
    return db_order


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


@router.post("/webhook/")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers["stripe-signature"]
    event = None

    print(payload)
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "payment_link.updated":
        payment_link = event["data"]["object"]
        pretty = json.dumps(event["data"], indent=4)
        print(pretty)
    # ... handle other event types
    if event["type"] == "payment_intent.succeeded":
        print("Got a successful payment")
        pretty = json.dumps(event["data"], indent=4)
        print(pretty)
    else:
        print("Unhandled event type {}".format(event["type"]))

    return SuccessResponse(success=True)


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
