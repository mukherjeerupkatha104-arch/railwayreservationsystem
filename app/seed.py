from datetime import date, timedelta
from app.database import SessionLocal
from app.models import Seat, Train, User
from app.security import hash_password

def seed_database():
    db = SessionLocal()
    try:
        # Create demo admin if missing.
        admin = db.query(User).filter(User.email == "admin@railway.local").first()
        if not admin:
            db.add(User(
                name="Railway Admin",
                email="admin@railway.local",
                password_hash=hash_password("Admin@123"),
                role="ADMIN",
            ))
            db.commit()

        if db.query(Train).count() > 0:
            return

        tomorrow = date.today() + timedelta(days=1)
        trains = [
            Train(train_number="12345", name="Eastern Express", source="Kolkata",
                  destination="Delhi", departure_time="18:30", arrival_time="10:15",
                  travel_date=tomorrow),
            Train(train_number="15678", name="Ganga Superfast", source="Kolkata",
                  destination="Delhi", departure_time="20:00", arrival_time="12:30",
                  travel_date=tomorrow),
            Train(train_number="22334", name="City Link Express", source="Delhi",
                  destination="Kolkata", departure_time="17:45", arrival_time="09:30",
                  travel_date=tomorrow),
        ]
        db.add_all(trains)
        db.flush()

        for train in trains:
            for i in range(1, 7):
                db.add(Seat(train_id=train.id, coach="S1", seat_number=str(i),
                            seat_class="SL", fare=650.0, is_available=True))
            for i in range(1, 7):
                db.add(Seat(train_id=train.id, coach="A1", seat_number=str(i),
                            seat_class="3A", fare=1450.0, is_available=True))
        db.commit()
    finally:
        db.close()
