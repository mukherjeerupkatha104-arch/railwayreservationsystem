from fastapi import FastAPI
from app.database import Base, engine
from app.migrate import migrate
from app.seed import seed_database
from app.routers import auth, trains, bookings, admin

migrate()
Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title="Railway Reservation & Seat Management API",
    description="Portfolio-ready railway booking backend with authentication, admin controls, seat protection and business rules.",
    version="2.0.0",
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(trains.router, prefix="/trains", tags=["Trains"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/", tags=["Health"])
def root():
    return {"message": "Railway Reservation API is running", "docs": "/docs", "version": "2.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
