from datetime import date, timedelta


# ---------- Basic Tests ----------

def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["version"] == "2.0.0"


# ---------- Authentication Tests ----------

def test_register_user(client):
    email = "testuser_auto@example.com"

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "Test@123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == email
    assert data["name"] == "Test User"
    assert data["role"] == "CUSTOMER"


def test_login_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser_auto@example.com",
            "password": "Test@123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client, user_headers):
    response = client.get(
        "/auth/me",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["email"] == "testuser_auto@example.com"


def test_duplicate_registration(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "testuser_auto@example.com",
            "password": "Test@123",
        },
    )

    assert response.status_code == 409


# ---------- Train Tests ----------

def test_search_trains(client):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    response = client.get(
        "/trains/search",
        params={
            "source": "Kolkata",
            "destination": "Delhi",
            "travel_date": tomorrow,
        },
    )

    assert response.status_code == 200

    trains = response.json()

    assert len(trains) >= 1
    assert trains[0]["source"] == "Kolkata"
    assert trains[0]["destination"] == "Delhi"


def test_get_train(client):
    response = client.get("/trains/1")

    assert response.status_code == 200

    train = response.json()

    assert train["id"] == 1
    assert train["train_number"] == "12345"


def test_get_available_seats(client):
    response = client.get(
        "/trains/1/seats",
        params={"available_only": True},
    )

    assert response.status_code == 200

    seats = response.json()

    assert len(seats) > 0
    assert all(seat["is_available"] is True for seat in seats)


def test_get_seats_by_class(client):
    response = client.get(
        "/trains/1/seats",
        params={
            "seat_class": "SL",
            "available_only": True,
        },
    )

    assert response.status_code == 200

    seats = response.json()

    assert len(seats) > 0
    assert all(seat["seat_class"] == "SL" for seat in seats)


# ---------- Booking Tests ----------

def test_create_booking(client, user_headers):
    seats_response = client.get(
        "/trains/1/seats",
        params={"available_only": True},
    )

    assert seats_response.status_code == 200

    seats = seats_response.json()

    assert len(seats) > 0

    seat = seats[0]

    response = client.post(
        "/bookings",
        headers=user_headers,
        json={
            "train_id": 1,
            "seat_id": seat["id"],
            "passenger_name": "Test Passenger",
            "passenger_age": 22,
            "passenger_gender": "Female",
        },
    )

    assert response.status_code == 201

    booking = response.json()

    assert "pnr" in booking
    assert booking["status"] == "CONFIRMED"
    assert booking["train"]["id"] == 1
    assert booking["seat"]["id"] == seat["id"]


def test_my_bookings(client, user_headers):
    response = client.get(
        "/bookings/my",
        headers=user_headers,
    )

    assert response.status_code == 200

    bookings = response.json()

    assert isinstance(bookings, list)


# ---------- Booking Cancellation & Rebooking ----------

def test_cancel_and_rebook(client, user_headers):
    seats_response = client.get(
        "/trains/1/seats",
        params={"available_only": True},
    )

    assert seats_response.status_code == 200

    seats = seats_response.json()

    assert len(seats) > 0

    seat = seats[0]

    # Book a seat
    booking_response = client.post(
        "/bookings",
        headers=user_headers,
        json={
            "train_id": 1,
            "seat_id": seat["id"],
            "passenger_name": "Rebooking Test",
            "passenger_age": 25,
            "passenger_gender": "Female",
        },
    )

    assert booking_response.status_code == 201

    booking = booking_response.json()
    pnr = booking["pnr"]

    # Verify seat is now unavailable
    seats_response = client.get(
        "/trains/1/seats",
        params={"available_only": True},
    )

    available_ids = [s["id"] for s in seats_response.json()]

    assert seat["id"] not in available_ids

    # Cancel the booking
    cancel_response = client.delete(
        f"/bookings/{pnr}",
        headers=user_headers,
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"

    # Verify seat becomes available again
    seats_response = client.get(
        "/trains/1/seats",
        params={"available_only": True},
    )

    available_ids = [s["id"] for s in seats_response.json()]

    assert seat["id"] in available_ids

    # Rebook the released seat
    rebook_response = client.post(
        "/bookings",
        headers=user_headers,
        json={
            "train_id": 1,
            "seat_id": seat["id"],
            "passenger_name": "Rebooking Test",
            "passenger_age": 25,
            "passenger_gender": "Female",
        },
    )

    assert rebook_response.status_code == 201

    rebooked = rebook_response.json()

    assert rebooked["status"] == "CONFIRMED"
    assert rebooked["seat"]["id"] == seat["id"]


# ---------- Authorization Tests ----------

def test_booking_requires_login(client):
    response = client.get("/bookings/my")

    assert response.status_code in [401, 403]


def test_admin_endpoint_requires_admin(client, user_headers):
    response = client.get(
        "/admin/users",
        headers=user_headers,
    )

    assert response.status_code == 403


def test_admin_list_users(client, admin_headers):
    response = client.get(
        "/admin/users",
        headers=admin_headers,
    )

    assert response.status_code == 200

    users = response.json()

    assert isinstance(users, list)


def test_admin_train_occupancy(client, admin_headers):
    response = client.get(
        "/admin/trains/1/occupancy",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["train_id"] == 1
    assert "total_seats" in data
    assert "available_seats" in data
    assert "booked_seats" in data
    assert "occupancy_percentage" in data


# ---------- Edge Case & Business Rule Tests ----------

def test_booking_already_booked_seat(client, user_headers):
    seats_response = client.get(
        "/trains/1/seats",
        params={"available_only": True},
    )

    assert seats_response.status_code == 200

    seats = seats_response.json()

    assert len(seats) > 0

    seat = seats[0]

    booking_data = {
        "train_id": 1,
        "seat_id": seat["id"],
        "passenger_name": "Seat Test",
        "passenger_age": 25,
        "passenger_gender": "Female",
    }

    # First booking should succeed
    first_response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_data,
    )

    assert first_response.status_code == 201

    # Same seat should now be rejected
    second_response = client.post(
        "/bookings",
        headers=user_headers,
        json=booking_data,
    )

    assert second_response.status_code == 409


def test_booking_seat_from_wrong_train(client, user_headers):
    # Get a seat from train 1
    seats_response = client.get(
        "/trains/1/seats",
        params={"available_only": True},
    )

    assert seats_response.status_code == 200

    seats = seats_response.json()

    assert len(seats) > 0

    seat = seats[0]

    # Try using that seat for train 2
    response = client.post(
        "/bookings",
        headers=user_headers,
        json={
            "train_id": 2,
            "seat_id": seat["id"],
            "passenger_name": "Wrong Train Test",
            "passenger_age": 25,
            "passenger_gender": "Female",
        },
    )

    assert response.status_code == 409


def test_booking_nonexistent_train(client, user_headers):
    response = client.post(
        "/bookings",
        headers=user_headers,
        json={
            "train_id": 99999,
            "seat_id": 1,
            "passenger_name": "Invalid Train",
            "passenger_age": 25,
            "passenger_gender": "Female",
        },
    )

    assert response.status_code == 404


def test_cancel_booking_twice(client, user_headers):
    seats_response = client.get(
        "/trains/1/seats",
        params={"available_only": True},
    )

    assert seats_response.status_code == 200

    seats = seats_response.json()

    assert len(seats) > 0

    seat = seats[0]

    booking_response = client.post(
        "/bookings",
        headers=user_headers,
        json={
            "train_id": 1,
            "seat_id": seat["id"],
            "passenger_name": "Cancel Test",
            "passenger_age": 25,
            "passenger_gender": "Female",
        },
    )

    assert booking_response.status_code == 201

    pnr = booking_response.json()["pnr"]

    # First cancellation
    first_cancel = client.delete(
        f"/bookings/{pnr}",
        headers=user_headers,
    )

    assert first_cancel.status_code == 200
    assert first_cancel.json()["status"] == "CANCELLED"

    # Second cancellation should fail
    second_cancel = client.delete(
        f"/bookings/{pnr}",
        headers=user_headers,
    )

    assert second_cancel.status_code == 409


def test_get_nonexistent_booking(client, user_headers):
    response = client.get(
        "/bookings/INVALIDPNR999",
        headers=user_headers,
    )

    assert response.status_code == 404


def test_get_nonexistent_train(client):
    response = client.get("/trains/99999")

    assert response.status_code == 404


def test_customer_cannot_create_train(client, user_headers):
    train_number = "UNAUTH" + date.today().strftime("%m%d")

    response = client.post(
        "/admin/trains",
        headers=user_headers,
        json={
            "train_number": train_number,
            "name": "Unauthorized Train",
            "source": "Kolkata",
            "destination": "Delhi",
            "departure_time": "10:00",
            "arrival_time": "18:00",
            "travel_date": (
                date.today() + timedelta(days=2)
            ).isoformat(),
        },
    )

    assert response.status_code == 403


def test_admin_create_train(client, admin_headers):
    train_number = "TEST" + date.today().strftime("%m%d")

    response = client.post(
        "/admin/trains",
        headers=admin_headers,
        json={
            "train_number": train_number,
            "name": "Automated Test Express",
            "source": "Kolkata",
            "destination": "Delhi",
            "departure_time": "10:00",
            "arrival_time": "18:00",
            "travel_date": (
                date.today() + timedelta(days=2)
            ).isoformat(),
        },
    )

    assert response.status_code == 201

    train = response.json()

    assert train["train_number"] == train_number
    assert train["name"] == "Automated Test Express"
    assert train["is_active"] is True


def test_admin_deactivate_train(client, admin_headers):
    # Create a temporary train
    train_number = "DEACT" + date.today().strftime("%m%d")

    create_response = client.post(
        "/admin/trains",
        headers=admin_headers,
        json={
            "train_number": train_number,
            "name": "Deactivate Test Express",
            "source": "Kolkata",
            "destination": "Delhi",
            "departure_time": "11:00",
            "arrival_time": "19:00",
            "travel_date": (
                date.today() + timedelta(days=2)
            ).isoformat(),
        },
    )

    assert create_response.status_code == 201

    train_id = create_response.json()["id"]

    # Deactivate the train
    response = client.patch(
        f"/admin/trains/{train_id}/deactivate",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Inactive train should no longer be publicly accessible
    public_response = client.get(f"/trains/{train_id}")

    assert public_response.status_code == 404