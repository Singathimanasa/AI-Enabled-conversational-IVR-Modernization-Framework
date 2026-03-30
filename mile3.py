from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI()

# -------------------------------
# Session storage
# -------------------------------

sessions = {}

class UserInput(BaseModel):
    session_id: str
    text: str


# -------------------------------
# Intent Detection
# -------------------------------

def detect_intent(text):
    text = text.lower()

    if "book" in text or "ticket" in text:
        return "booking"

    if "pnr" in text or "status" in text:
        return "pnr_status"

    if "running" in text or "train status" in text:
        return "train_status"

    return "unknown"


# -------------------------------
# Start IVR Conversation
# -------------------------------

@app.get("/ivr/start")
def start_ivr():

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "state": "welcome",
        "data": {}
    }

    return {
        "session_id": session_id,
        "message": "Welcome to IRCTC IVR 🚆. How can I help you today?"
    }


# -------------------------------
# Handle Conversation
# -------------------------------

@app.post("/ivr/chat")
def chat(user_input: UserInput):

    session = sessions.get(user_input.session_id)

    if not session:
        return {"message": "Invalid session. Please restart IVR."}

    state = session["state"]
    text = user_input.text

    # ---------------------------
    # Step 1: Detect intent
    # ---------------------------

    if state == "welcome":

        intent = detect_intent(text)

        if intent == "booking":
            session["state"] = "get_source"

            return {
                "message": "Sure! From which station are you travelling?"
            }

        elif intent == "pnr_status":
            session["state"] = "get_pnr"

            return {
                "message": "Please enter your PNR number."
            }

        elif intent == "train_status":
            session["state"] = "get_train_number"

            return {
                "message": "Please enter your train number."
            }

        else:
            return {
                "message": "Sorry, I didn't understand. You can say book ticket, check PNR, or train status."
            }

    # ---------------------------
    # Booking flow
    # ---------------------------

    elif state == "get_source":

        session["data"]["source"] = text
        session["state"] = "get_destination"

        return {
            "message": f"Travelling from {text}. Where would you like to go?"
        }

    elif state == "get_destination":

        session["data"]["destination"] = text
        session["state"] = "get_date"

        return {
            "message": f"Travelling to {text}. What is your travel date?"
        }

    elif state == "get_date":

        session["data"]["date"] = text
        session["state"] = "complete"

        return {
            "message": f"Searching trains from {session['data']['source']} to {session['data']['destination']} on {text}. Booking feature coming soon!"
        }

    # ---------------------------
    # PNR flow
    # ---------------------------

    elif state == "get_pnr":

        return {
            "message": f"PNR {text} is currently WAITLIST 5."
        }

    # ---------------------------
    # Train running status
    # ---------------------------

    elif state == "get_train_number":

        return {
            "message": f"Train {text} is running on time."
        }

    return {"message": "Conversation ended."}