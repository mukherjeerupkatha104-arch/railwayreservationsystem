from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models import Seat, Train, User
from app.schemas import TrainCreate, TrainResponse

router = APIRouter()

@router.post("/trains", response_model=TrainResponse, status_code=201)
def create_train(
    payload: TrainCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if db.query(Train).filter(Train.train_number == payload.train_number).first():
        raise HTTPException(status_code=409, detail="Train number already exists")

    train = Train(**payload.model_dump(), is_active=True)
    db.add(train)
    db.commit()
    db.refresh(train)
    return train

@router.patch("/trains/{train_id}/deactivate", response_model=TrainResponse)
def deactivate_train(
    train_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    train = db.get(Train, train_id)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")
    train.is_active = False
    db.commit()
    db.refresh(train)
    return train

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    users = db.query(User).order_by(User.id).all()
    return [
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
        for u in users
    ]

@router.get("/trains/{train_id}/occupancy")
def train_occupancy(
    train_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    train = db.get(Train, train_id)
    if not train:
        raise HTTPException(status_code=404, detail="Train not found")

    total = db.query(Seat).filter(Seat.train_id == train_id).count()
    available = db.query(Seat).filter(
        Seat.train_id == train_id, Seat.is_available.is_(True)
    ).count()

    return {
        "train_id": train.id,
        "train_number": train.train_number,
        "total_seats": total,
        "available_seats": available,
        "booked_seats": total - available,
        "occupancy_percentage": round(((total - available) / total) * 100, 2) if total else 0,
    }
