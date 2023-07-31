from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from .auth import get_current_user
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from models import Inventory, Partner
from database import get_db, Item, SourceItem
from sqlalchemy.orm import Session
import pandas as pd
from typing import List
import io

router = APIRouter()


@router.get("/test/")
async def root():
    return {"message": "Hello World"}


@router.get("/{item_id}")
async def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.get("/list/")
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_items = db.query(Inventory).offset(skip).limit(limit).all()
    return db_items


get_current_partner = Depends(get_current_user)


@router.get("/list/json/{token}")
async def all_items(token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Partner token is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        credentials_exception.detail = "No token provided"
        raise credentials_exception
    partner = db.query(Partner).filter(Partner.api_key == token).first()
    if partner is None:
        raise credentials_exception
    all_items = db.query(Inventory).all()
    return {"partner": partner.name, "items": all_items}


@router.post("/customsheet/")
async def create_custom_sheet(ids: List[int], db: Session = Depends(get_db)):
    items = db.query(Inventory).filter(Inventory.id.in_(ids)).all()
    df = pd.DataFrame([item.__dict__ for item in items])
    df = df.drop(columns=["_sa_instance_state"])
    df.to_excel("custom.xlsx", index=False)
    filename = "custom.xlsx"
    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/latestsheet/")
async def create_latest_sheet(db: Session = Depends(get_db)):
    all_items = db.query(Inventory).all()
    df = pd.DataFrame([item.__dict__ for item in all_items])
    df = df.drop(columns=["_sa_instance_state"])
    df.to_excel("latest.xlsx", index=False)
    filename = "latest.xlsx"
    return FileResponse(
        filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post("/")
async def create_item(item: Item, db: Session = Depends(get_db)):
    print("here is the thing passed to me")
    print(item)
    new_inventory = Inventory(
        upc=item.upc,
        description=item.description,
        price=item.price,
        in_stock=10,
        mfr_part=item.mfr_part,
        manufacturer=item.manufacturer,
        category="test",
        condition="new",
    )
    db.add(new_inventory)
    db.commit()
    return item


def create_items(items: List[SourceItem], db: Session, markup: float):
    print("here is the thing passed to me")
    new_items = []
    print(items[0])
    for item in items:
        item_dict = dict(item, by_alias=True)
        # print(item_dict)
        price = float(item.get("Price Rebate applied", 0))  # Ensure price is a float

        markup_price = round(price * (1 + (float(markup) / 100)), 2)
        print(markup_price)
        new_inventory = Inventory(
            upc=item_dict["UPC"],
            description=item_dict["Long Description"],
            price=markup_price,
            in_stock=item_dict["In Stock"],
            on_order=item_dict["On Order"],
            mfr_part=item_dict["MFG Part#"],
            manufacturer=item_dict["MFR"],
            category=item_dict["Product Category"],
            condition=item_dict["Condition"],
        )
        new_items.append(new_inventory)
    # db.add(new_inventory)
    db.bulk_save_objects(new_items)
    db.commit()
    return new_items


@router.get("/search/")
async def test_query(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@router.post("/uploadfile/")
async def create_upload_file(
    markup: float = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    # body = await request.body()
    # print(body)
    print("here is the markup")
    print(markup)
    # print("here is the file")
    # print(file.filename for file in files)
    db.query(Inventory).delete()
    db.commit()
    # first we should drop the entire database and recreate it
    for file in files:
        try:
            extension = file.filename.split(".")[-1] in ("xlsx", "xls", "xlsm")
            if not extension:
                return JSONResponse(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    content="Invalid file type",
                )
            df = pd.read_excel(
                io.BytesIO(file.file.read()),
                engine="openpyxl",
                skiprows=range(0, 9),
                dtype={"UPC": "str", "Rebate": "str"},
            )

            # for index, row in df.iterrows():
            #     create_an_item(row, db)

            create_items(df.to_dict(orient="records"), db, markup)

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error {e}")
    return {"filenames": [file.filename for file in files]}
