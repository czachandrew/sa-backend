from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()


class Item(BaseModel):
    id: int
    upc: str
    description: str | None = None
    price: float
    in_stock: float | None = None
    on_order: float | None = None
    mfr_part: str | None = None
    manufacturer: str | None = None
    category: str | None = None
    condition: str | None = None


class CreateOrderItem(BaseModel):
    quantity: int
    item: Item


class SourceItem(BaseModel):
    UPC: str
    Long_Description: str = Field(None, alias="Long Description")
    Price_Rebate_Applied: float = Field(..., alias="Price Rebate Applied")
    In_Stock: int = Field(None, alias="In Stock")
    On_Order: int = Field(None, alias="On Order")
    MFG_Part: str = Field(None, alias="MFG Part#")
    MFR: str | None
    Product_Category: str = Field(None, alias="Product Category")
    Condition: str | None


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres", "postgresql")
database = Database(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
