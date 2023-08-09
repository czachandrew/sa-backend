from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status, Header
from models import User as UserModel
from models import Partner
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class PartnerCreate(BaseModel):
    name: str


class User(UserBase):
    id: Optional[int]

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginPayload(BaseModel):
    username: str
    password: str


SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 43200

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_long_lived_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=365
        )  # 1 year long token for example
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    to_encode.update({"type": "refresh"})
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/token/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshRequest, db: Session = Depends(get_db)):
    refresh_token = refresh_request.refresh_token

    def raise_exception(detail: str):
        raise HTTPException(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True},
        )
        email: str = payload.get("sub")
        if email is None:
            raise_exception("Email not found in token")

        if payload.get("type") != "refresh":  # Check if token type is refresh
            raise_exception("Invalid token type")

        token_data = TokenData(email=email)
    except JWTError:
        raise_exception("Could not decode token")

    user = await get_user(db, email=token_data.email)
    if user is None:
        raise_exception("User not found")

    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/token", response_model=Token)
async def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = await get_user(db, payload.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    print("here are the access and refresh tokens")
    print(access_token)
    print(refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me/")
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/create_partner/")
async def create_partner(partner: PartnerCreate, db: Session = Depends(get_db)):
    print("here is the name passed to the server")
    print(partner.name)
    token = create_long_lived_token(data={"sub": partner.name})
    new_partner = Partner(name=partner.name, api_key=token)
    db.add(new_partner)
    db.commit()
    db.refresh(new_partner)
    return new_partner


@router.post("/generate_partner_token/{partner_id}")
async def generate_partner_token(
    partner_id: int, db: Session = Depends(get_db)
):  # insert necessary parameters, like the partner's ID
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")

    token = create_long_lived_token(data={"sub": partner_id})
    try:
        partner.api_key = token
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="An error occurred while trying to generate the token. Please try again.",
        ) from e

    return {"access_token": token, "token_type": "bearer"}


@router.get("/testheroku/")
async def test_heroku():
    return {"message": "Hello from Heroku"}


@router.post("/register/")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system",
        )

    new_user = UserModel(
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
