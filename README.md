# Railway Reservation API

A backend REST API for a Railway Reservation System built with **FastAPI, Python, SQLAlchemy, SQLite, and JWT authentication**.

The project provides separate customer and admin functionality, including train search, seat availability, booking, cancellation, rebooking, train management, and automated API testing.

---

## Features

### Customer Features

* User registration and login
* JWT-based authentication
* View current user profile
* Search trains by source, destination, and travel date
* View train details
* View available seats
* Filter seats by class
* Book a seat
* View personal bookings
* Cancel a booking
* Rebook a released seat
* Prevent duplicate booking of the same seat
* Prevent booking a seat belonging to another train

### Admin Features

* Admin authentication
* View registered users
* Create trains
* Deactivate trains
* View train occupancy
* Monitor total, available, and booked seats
* Role-based access control

### Testing

* Automated API testing with Pytest
* Authentication testing
* Authorization testing
* Train API testing
* Booking workflow testing
* Cancellation and rebooking testing
* Business-rule validation
* Edge-case testing
* HTML test report generation

---

## Tech Stack

| Technology   | Purpose                      |
| ------------ | ---------------------------- |
| Python       | Backend programming          |
| FastAPI      | REST API framework           |
| SQLAlchemy   | ORM and database interaction |
| SQLite       | Database                     |
| Pydantic     | Request/response validation  |
| JWT          | Authentication               |
| Pytest       | Automated testing            |
| pytest-html  | HTML test reports            |
| Uvicorn      | ASGI server                  |
| Swagger UI   | API documentation            |
| Git & GitHub | Version control              |

---

## Project Structure

```text
railway_reservation_api/
│
├── app/
│   ├── routers/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── bookings.py
│   │   ├── trains.py
│   │   └── __init__.py
│   │
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── migrate.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── seed.py
│   └── __init__.py
│
├── tests/
│   ├── conftest.py
│   └── test_api.py
│
├── reports/
│   └── test_report.html
│
├── railway.db
├── railway_backup.db
├── test_railway.db
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mukherjeerupkatha104-arch/railwayreservationsystem.git
cd railway_reservation_api
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

#### Windows CMD

```cmd
venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Configuration

The application uses SQLite by default.

The default database configuration is:

```text
sqlite:///./railway.db
```

A `.env.example` file is included for environment-specific configuration.

---

## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Swagger UI can be used to execute and test the API endpoints directly from the browser.

---

## Authentication

The application uses **JWT Bearer Token authentication**.

### Login

```text
POST /auth/login
```

After successful login, the API returns an access token.

Use the token in authenticated requests:

```text
Authorization: Bearer <access_token>
```

The application supports two roles:

```text
CUSTOMER
ADMIN
```

Customer users can access customer-specific functionality, while administrative endpoints require the `ADMIN` role.

---

## Main API Endpoints

### Authentication

| Method | Endpoint         | Description                 |
| ------ | ---------------- | --------------------------- |
| POST   | `/auth/register` | Register a new customer     |
| POST   | `/auth/login`    | Login and receive JWT token |
| GET    | `/auth/me`       | Get current user            |

### Trains

| Method | Endpoint                   | Description       |
| ------ | -------------------------- | ----------------- |
| GET    | `/trains/search`           | Search trains     |
| GET    | `/trains/{train_id}`       | Get train details |
| GET    | `/trains/{train_id}/seats` | Get train seats   |

### Bookings

| Method | Endpoint          | Description                  |
| ------ | ----------------- | ---------------------------- |
| POST   | `/bookings`       | Create a booking             |
| GET    | `/bookings/my`    | View current user's bookings |
| GET    | `/bookings/{pnr}` | View booking by PNR          |
| DELETE | `/bookings/{pnr}` | Cancel booking               |

### Admin

| Method | Endpoint                              | Description          |
| ------ | ------------------------------------- | -------------------- |
| GET    | `/admin/users`                        | View users           |
| POST   | `/admin/trains`                       | Create a train       |
| PATCH  | `/admin/trains/{train_id}/deactivate` | Deactivate a train   |
| GET    | `/admin/trains/{train_id}/occupancy`  | View train occupancy |

---

## Booking Workflow

The main customer workflow is:

```text
Register
   ↓
Login
   ↓
Search Train
   ↓
View Available Seats
   ↓
Select Seat
   ↓
Create Booking
   ↓
Receive PNR
   ↓
View Booking
   ↓
Cancel Booking
   ↓
Seat Becomes Available
   ↓
Rebook Released Seat
```

The system validates important business rules during the workflow.

---

## Business Rules

The API prevents:

* Booking without authentication
* Booking an already occupied seat
* Booking a seat belonging to another train
* Accessing another user's booking without authorization
* Customer access to admin endpoints
* Cancelling an already cancelled booking
* Accessing inactive or nonexistent trains

---

## Automated Testing

The project includes automated API tests using **Pytest**.

Run the complete test suite:

```bash
python -m pytest -v
```

The test suite covers:

* Health endpoint
* Root endpoint
* User registration
* User login
* Current-user authentication
* Duplicate registration
* Train search
* Train details
* Seat availability
* Seat-class filtering
* Booking creation
* Personal bookings
* Booking cancellation
* Rebooking
* Duplicate seat booking
* Wrong-train seat validation
* Invalid train handling
* Invalid booking handling
* Double cancellation
* Customer/admin authorization
* Admin train creation
* Train deactivation
* Train occupancy

### Current Test Result

```text
26 passed
```

---

## HTML Test Report

Generate a detailed HTML test report using:

```bash
python -m pytest -v --html=reports/test_report.html --self-contained-html
```

The generated report is located at:

```text
reports/test_report.html
```

The report provides a browser-based summary of the automated test execution.

---

## Sample Credentials

### Admin

```text
Email: admin@railway.local
Password: Admin@123
Role: ADMIN
```

### Test Customer

```text
Email: testuser_auto@example.com
Password: Test@123
Role: CUSTOMER
```

> These credentials are intended for local development and testing only.

---

## Sample Trains

The application includes seeded demo trains for testing.

| Train | Name              | Source  | Destination |
| ----- | ----------------- | ------- | ----------- |
| 12345 | Eastern Express   | Kolkata | Delhi       |
| 15678 | Ganga Superfast   | Kolkata | Delhi       |
| 22334 | City Link Express | Delhi   | Kolkata     |

Each seeded train includes seats across different classes.

---

## Error Handling

The API uses appropriate HTTP status codes for common situations, including:

```text
200 OK
201 Created
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
```

This helps clients understand whether a request succeeded or why it failed.

---

## Database

The project uses **SQLite** with **SQLAlchemy ORM**.

Main entities include:

```text
User
Train
Seat
Booking
```

Relationships between these entities are used to manage users, trains, seats, and reservations.

Automated tests use a separate database:

```text
test_railway.db
```

This prevents test execution from modifying the main development database.

---

## Future Improvements

Possible future enhancements include:

* PostgreSQL support
* Docker containerization
* CI/CD with GitHub Actions
* Email booking confirmation
* Payment integration
* Waiting-list functionality
* Multiple passengers per booking
* Seat-class based pricing
* Pagination for large datasets
* API rate limiting
* Production deployment
* Frontend integration

---

## Project Highlights

This project demonstrates practical backend development skills including:

* REST API development
* FastAPI
* Python
* SQLAlchemy
* Database design
* JWT authentication
* Role-based authorization
* CRUD operations
* Business-rule validation
* Error handling
* Automated testing
* Test reporting
* API documentation
* Environment-based configuration

---

## Author

**Rupkatha Mukharjee**

Computer Science Engineering Student

---

