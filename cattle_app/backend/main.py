import os
import shutil
from typing import List

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from auth import authenticate_user, create_access_token, get_current_user, hash_password, require_role
from database import Base, engine, get_db
from ml import predict_breed
from models import Cattle, Notification, Order, User
from notify import push_notification

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cattle Marketplace API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class CattleOut(BaseModel):
    id: int
    title: str
    price: float
    image_path: str | None
    predicted_breed: str | None
    is_sold: bool
    seller_id: int

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: bool

    class Config:
        from_attributes = True


@app.get("/")
def health_check():
    return {"message": "Cattle Marketplace backend running"}


@app.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if payload.role not in {"admin", "seller", "buyer"}:
        raise HTTPException(status_code=400, detail="Role must be admin/seller/buyer")
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@app.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email/password")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "name": user.name}


@app.post("/cattle", response_model=CattleOut)
def add_cattle(
    title: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    seller: User = Depends(require_role("seller", "admin")),
):
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    breed = predict_breed(file_path)
    cattle = Cattle(title=title, price=price, image_path=file_path, predicted_breed=breed, seller_id=seller.id)
    db.add(cattle)
    db.commit()
    db.refresh(cattle)
    return cattle


@app.get("/cattle", response_model=List[CattleOut])
def list_cattle(db: Session = Depends(get_db)):
    return db.query(Cattle).all()


@app.post("/buy/{cattle_id}")
def buy_cattle(
    cattle_id: int,
    db: Session = Depends(get_db),
    buyer: User = Depends(require_role("buyer", "admin")),
):
    cattle = db.query(Cattle).filter(Cattle.id == cattle_id).first()
    if not cattle:
        raise HTTPException(status_code=404, detail="Cattle not found")
    if cattle.is_sold:
        raise HTTPException(status_code=400, detail="Already sold")

    order = Order(cattle_id=cattle.id, buyer_id=buyer.id, amount=cattle.price, payment_status="paid")
    cattle.is_sold = True
    db.add(order)
    db.commit()

    push_notification(
        db,
        user_id=cattle.seller_id,
        message=f"Your cattle '{cattle.title}' was purchased by {buyer.name}. Dummy payment marked as paid.",
    )

    return {"message": "Purchase successful", "order_id": order.id, "payment": "dummy-paid"}


@app.get("/notifications", response_model=List[NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
