from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="CUSTOMER", nullable=False)
    bookings = relationship("Booking", back_populates="user")

class Train(Base):
    __tablename__ = "trains"
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    source = Column(String(100), nullable=False, index=True)
    destination = Column(String(100), nullable=False, index=True)
    departure_time = Column(String(20), nullable=False)
    arrival_time = Column(String(20), nullable=False)
    travel_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    seats = relationship("Seat", back_populates="train", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="train")

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)
    coach = Column(String(10), nullable=False)
    seat_number = Column(String(10), nullable=False)
    seat_class = Column(String(10), nullable=False)
    fare = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    train = relationship("Train", back_populates="seats")
    booking = relationship("Booking", back_populates="seat", uselist=False)
    __table_args__ = (
        UniqueConstraint("train_id", "coach", "seat_number", name="uq_train_seat"),
    )

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    pnr = Column(String(20), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)
    passenger_name = Column(String(100), nullable=False)
    passenger_age = Column(Integer, nullable=False)
    passenger_gender = Column(String(20), nullable=False)
    status = Column(String(20), default="CONFIRMED", nullable=False)
    amount = Column(Float, nullable=False)
    booked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="bookings")
    train = relationship("Train", back_populates="bookings")
    seat = relationship("Seat", back_populates="booking")
