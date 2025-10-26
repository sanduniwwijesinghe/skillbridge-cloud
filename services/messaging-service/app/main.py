from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database
from .database import SessionLocal, engine
from pydantic import BaseModel
from datetime import datetime
from typing import List
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wait for DB
logger.info("Waiting for database...")
is_db_ready = False
for _ in range(30):
    try:
        db_conn = engine.connect()
        db_conn.close()
        is_db_ready = True
        logger.info("Database is ready!")
        break
    except Exception as e:
        logger.warning(f"Database not ready yet, retrying... Error: {e}")
        time.sleep(1)
if not is_db_ready:
    logger.error("Database connection failed.")

try:
    logger.info("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")
except Exception as e:
     logger.error(f"Error creating tables: {e}")

app = FastAPI()

# Pydantic models
class MessageCreate(BaseModel):
    sender_id: int # Get from auth token later
    receiver_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "Messaging-Service is running"}

@app.post("/", response_model=MessageOut)
def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to send message from {message.sender_id} to {message.receiver_id}")
    try:
        # Add checks later: Does receiver exist? Can sender message receiver?
        db_message = models.Message(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            content=message.content
        )
        logger.info("Adding message to session...")
        db.add(db_message)
        logger.info("Committing transaction...")
        db.commit()
        logger.info("Refreshing message object...")
        db.refresh(db_message)
        logger.info(f"Message sent successfully: {db_message.id}")
        return db_message
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error sending message")

@app.get("/conversation/{user1_id}/{user2_id}", response_model=List[MessageOut])
def get_conversation(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching conversation between {user1_id} and {user2_id}")
    try:
        # Add checks later: Is requesting user one of the participants?
        messages = db.query(models.Message).filter(
            ((models.Message.sender_id == user1_id) & (models.Message.receiver_id == user2_id)) |
            ((models.Message.sender_id == user2_id) & (models.Message.receiver_id == user1_id))
        ).order_by(models.Message.timestamp.asc()).all()
        logger.info(f"Found {len(messages)} messages")
        return messages
    except Exception as e:
        logger.error(f"Error fetching conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error fetching conversation")

