from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI(title="SkillBridge - Booking Service", version="0.1.0")

class Booking(BaseModel):
    id: int
    mentor_id: int
    mentee_id: int
    start: datetime
    end: datetime
    status: str = "pending"

BOOKINGS: List[Booking] = []

@app.get("/health")
def health(): return {"ok": True}

@app.get("/bookings")
def list_bookings(): return BOOKINGS

@app.post("/bookings")
def create_booking(b: Booking):
    BOOKINGS.append(b)
    return {"created": b}

@app.post("/bookings/{booking_id}/confirm")
def confirm_booking(booking_id: int):
    for b in BOOKINGS:
        if b.id == booking_id:
            b.status = "confirmed"
            return {"ok": True, "booking": b}
    return {"ok": False, "error": "not_found"}
