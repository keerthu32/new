from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin | seller | buyer

    cattle = relationship("Cattle", back_populates="seller", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")


class Cattle(Base):
    __tablename__ = "cattle"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image_path = Column(String, nullable=True)
    predicted_breed = Column(String, nullable=True)
    is_sold = Column(Boolean, default=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    seller = relationship("User", back_populates="cattle")
    orders = relationship("Order", back_populates="cattle", cascade="all, delete")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    cattle_id = Column(Integer, ForeignKey("cattle.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_status = Column(String, default="paid")
    created_at = Column(DateTime, default=datetime.utcnow)

    cattle = relationship("Cattle", back_populates="orders")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
