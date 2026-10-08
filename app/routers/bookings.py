import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Booking, Seat, Train, User
from app.schemas import BookingCreate, BookingResponse

router = APIRouter()

def generate_pnr():
    return str(secrets.randbelow(9_000_000_000) + 1_000_000_000)

@router.post("", response_model=BookingResponse, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    train = db.get(Train, payload.train_id)
    if not train or not train.is_active:
        raise HTTPException(status_code=404, detail="Train not found or inactive")

    # Business rule: bookings cannot be made after the travel date.
    from datetime import date
    if train.travel_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot book a past journey")

    result = db.execute(
        update(Seat)
        .where(
            Seat.id == payload.seat_id,
            Seat.train_id == payload.train_id,
            Seat.is_available.is_(True),
        )
        .values(is_available=False)
    )

    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat is unavailable or does not belong to this train",
        )

    seat = db.get(Seat, payload.seat_id)

    for _ in range(5):
        pnr = generate_pnr()
        if not db.query(Booking).filter(Booking.pnr == pnr).first():
            break
    else:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not generate PNR")

    booking = Booking(
        pnr=pnr, user_id=current_user.id, train_id=train.id, seat_id=seat.id,
        passenger_name=payload.passenger_name, passenger_age=payload.passenger_age,
        passenger_gender=payload.passenger_gender, amount=seat.fare,
        status="CONFIRMED",
    )
    try:
        db.add(booking)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Booking could not be completed")

    return (
        db.query(Booking)
        .options(joinedload(Booking.train), joinedload(Booking.seat))
        .filter(Booking.id == booking.id)
        .first()
    )

@router.get("/my", response_model=list[BookingResponse])
def my_bookings(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return (
        db.query(Booking)
        .options(joinedload(Booking.train), joinedload(Booking.seat))
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.booked_at.desc())
        .all()
    )

@router.get("/{pnr}", response_model=BookingResponse)
def get_booking(pnr: str, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.train), joinedload(Booking.seat))
        .filter(Booking.pnr == pnr, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.delete("/{pnr}", response_model=BookingResponse)
def cancel_booking(pnr: str, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.train), joinedload(Booking.seat))
        .filter(Booking.pnr == pnr, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "CANCELLED":
        raise HTTPException(status_code=409, detail="Booking is already cancelled")

    booking.status = "CANCELLED"
    booking.seat.is_available = True
    db.commit()
    db.refresh(booking)
    return booking
