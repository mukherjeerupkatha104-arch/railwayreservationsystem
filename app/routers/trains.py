from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Seat, Train
from app.schemas import SeatResponse, TrainResponse

router = APIRouter()

@router.get("/search", response_model=list[TrainResponse])
def search_trains(
    source: str = Query(min_length=2),
    destination: str = Query(min_length=2),
    travel_date: date = Query(...),
    db: Session = Depends(get_db),
):
    return (
        db.query(Train)
        .filter(
            func.lower(Train.source) == source.lower(),
            func.lower(Train.destination) == destination.lower(),
            Train.travel_date == travel_date,
            Train.is_active.is_(True),
        )
        .all()
    )

@router.get("/{train_id}", response_model=TrainResponse)
def get_train(train_id: int, db: Session = Depends(get_db)):
    train = db.get(Train, train_id)
    if not train or not train.is_active:
        raise HTTPException(status_code=404, detail="Active train not found")
    return train

@router.get("/{train_id}/seats", response_model=list[SeatResponse])
def get_seats(
    train_id: int,
    seat_class: str | None = None,
    available_only: bool = True,
    db: Session = Depends(get_db),
):
    train = db.get(Train, train_id)
    if not train or not train.is_active:
        raise HTTPException(status_code=404, detail="Active train not found")

    query = db.query(Seat).filter(Seat.train_id == train_id)
    if seat_class:
        query = query.filter(func.lower(Seat.seat_class) == seat_class.lower())
    if available_only:
        query = query.filter(Seat.is_available.is_(True))
    return query.order_by(Seat.coach, Seat.seat_number).all()
