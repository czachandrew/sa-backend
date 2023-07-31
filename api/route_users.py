from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from .auth import get_password_hash, verify_password, create_access_token
from datetime import datetime, timedelta
from database import get_db
from sqlalchemy.orm import Session
from models import Partner

router = APIRouter()


@router.post("/register/")
async def register_user():
    return {"message": "register user"}


@router.get("/partners/")
async def get_partners(db: Session = Depends(get_db)):
    partners = db.query(Partner).all()
    return partners


@router.get("/partners/kill/{partner_id}")
async def kill_partner(partner_id: int, db: Session = Depends(get_db)):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    db.delete(partner)
    db.commit()
    return {"message": "Partner deleted"}


# @router.post("/token/", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = get_user(fake_users_db, form_data.email)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     hashed_password = get_password_hash(form_data.password)
#     if not verify_password(form_data.password, hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.email}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}
