from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    upc = Column(String, nullable=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    in_stock = Column(Integer, nullable=True)
    on_order = Column(Integer, nullable=True)
    mfr_part = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    category = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    status = Column(String, nullable=False, default="good")

    order_items = relationship("OrderItem", back_populates="product")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    orders = relationship("Order", back_populates="user")


class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    api_key = Column(String, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total = Column(Float, nullable=True)
    payment_link = Column(String, nullable=True)
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=True
    )
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)
    quantity = Column(Integer, nullable=True)
    price = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    order = relationship("Order", back_populates="items")
    product = relationship("Inventory", back_populates="order_items")
