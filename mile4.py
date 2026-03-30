# irctc_ivr_web_simulator.py

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import time
import requests
import logging

# -----------------------------
# FASTAPI APPLICATION
# -----------------------------

app = FastAPI()

# simple in-memory session store
sessions = {}

# sample train database
trains = {
    "12951": {"name": "Mumbai Rajdhani"},
    "12302": {"name": "Howrah Rajdhani"}
}

logging.basicConfig(level=logging.INFO)


@app.get("/")
def root():
    return {"message": "Welcome to IRCTC IVR Web Simulator 🚆"}


# -----------------------------
# IVR START MENU
# -----------------------------
@app.get("/ivr/start")
def start_ivr():

    return {
        "menu": "Main Menu",
        "message": "Welcome to IRCTC IVR",
        "options": [
            {"key": "1", "text": "Book Train Ticket"},
            {"key": "2", "text": "PNR Status"},
            {"key": "3", "text": "Train Running Status"}
        ]
    }


# -----------------------------
# SESSION CREATION
# -----------------------------
@app.post("/ivr/session")
def create_session(call_id: str):

    sessions[call_id] = {"state": "main-menu"}

    return {"message": "Session created", "call_id": call_id}


# -----------------------------
# HANDLE MENU KEY PRESS
# -----------------------------
@app.post("/handle_key")
def handle_key(Digits: str, menu: str, call_id: str):

    if call_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if menu == "main-menu" and Digits == "1":

        sessions[call_id]["state"] = "booking-menu"

        return {
            "menu": "Booking Menu",
            "message": "Press 1 for General Booking"
        }

    if menu == "booking-menu" and Digits == "1":

        sessions[call_id]["state"] = "origin"

        return {
            "menu": "Origin Input",
            "message": "Enter source station"
        }

    return {"message": "Invalid option"}


# -----------------------------
# CONVERSATION FLOW
# -----------------------------
@app.post("/conversation_flow")
def conversation_flow(call_id: str, user_text: str):

    if call_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if "book" in user_text.lower():

        sessions[call_id]["state"] = "booking-menu"

        return {
            "menu": "Booking Menu",
            "message": "Where would you like to travel?"
        }

    return {"message": "Command not recognised"}


@app.post("/next_step")
def next_step(call_id: str, user_text: str):

    if call_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[call_id]["origin"] = user_text

    return {
        "message": f"Where would you like to travel from {user_text}?"
    }


# -----------------------------
# BOOKING API
# -----------------------------
@app.post("/submit_booking")
def submit_booking(data: dict):

    booking = {
        "booking_details": data
    }

    return booking


# -----------------------------
# TRAIN INFO API
# -----------------------------
@app.get("/train/{train_id}")
def get_train(train_id: str):

    if train_id not in trains:
        raise HTTPException(status_code=404, detail="Train not found")

    return trains[train_id]


# -----------------------------
# TEST CLIENT
# -----------------------------
client = TestClient(app)

# =====================================================
# 1️⃣ UNIT TESTS
# =====================================================

def test_root():

    resp = client.get("/")

    assert resp.status_code == 200
    assert "Welcome" in resp.json()["message"]


def test_submit_booking_valid():

    payload = {
        "booking_id": "IR123",
        "trans_id": "TX100",
        "passenger_fullname": "Rahul Sharma",
        "passenger_contact": "9999999999"
    }

    resp = client.post("/submit_booking", json=payload)

    assert resp.status_code == 200

    data = resp.json()

    assert data["booking_details"]["booking_id"] == "IR123"


# =====================================================
# 2️⃣ INTEGRATION TEST
# =====================================================

def test_conversation_booking_flow():

    call_id = "test_call_001"

    client.post("/ivr/session", params={"call_id": call_id})

    response = client.post(
        "/conversation_flow",
        params={
            "call_id": call_id,
            "user_text": "Book a train ticket"
        }
    )

    assert response.status_code == 200
    assert "Booking Menu" in response.json()["menu"]

    response = client.post(
        "/next_step",
        params={
            "call_id": call_id,
            "user_text": "Delhi"
        }
    )

    assert response.status_code == 200
    assert "Delhi" in response.json()["message"]


# =====================================================
# 3️⃣ END TO END TEST
# =====================================================

def test_full_ivr_flow():

    call_id = "ivr_user_002"

    start = client.get("/ivr/start")

    assert start.status_code == 200
    assert "Main Menu" in start.json()["menu"]

    client.post("/ivr/session", params={"call_id": call_id})

    handle = client.post(
        "/handle_key",
        params={
            "Digits": "1",
            "menu": "main-menu",
            "call_id": call_id
        }
    )

    assert "Booking Menu" in handle.json()["menu"]

    dom = client.post(
        "/handle_key",
        params={
            "Digits": "1",
            "menu": "booking-menu",
            "call_id": call_id
        }
    )

    assert dom.status_code == 200
    assert "Enter source station" in dom.json()["message"]

    print("E2E IVR Flow Completed")


# =====================================================
# 4️⃣ PERFORMANCE / LOAD TEST
# =====================================================

def load_test(num_requests=20):

    url = "http://localhost:8000/ivr/start"

    start_time = time.time()

    success = 0

    for i in range(num_requests):

        res = requests.get(url)

        if res.status_code == 200:
            success += 1

    total_time = time.time() - start_time

    print(f"Sent {num_requests} requests")
    print(f"Successful responses: {success}")
    print(f"Average response time: {total_time/num_requests:.2f} seconds")


# =====================================================
# 5️⃣ ERROR HANDLING TEST
# =====================================================

def test_invalid_train_id():

    response = client.get("/train/INVALID_ID")

    assert response.status_code == 404
    assert "Train not found" in response.json()["detail"]


# =====================================================
# RUN LOAD TEST MANUALLY
# =====================================================

if __name__ == "__main__":
    load_test(50)