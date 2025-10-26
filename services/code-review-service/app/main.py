from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database
from .database import SessionLocal, engine
from pydantic import BaseModel, HttpUrl
# --- FIX: Add missing import ---
from datetime import datetime
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
class CodeReviewCreate(BaseModel):
    mentor_id: int
    mentee_id: int # Get from auth token later
    repo_url: HttpUrl # Validate it's a URL

class CodeReviewOut(BaseModel):
    id: int
    mentor_id: int
    mentee_id: int
    repo_url: HttpUrl
    status: str
    created_at: datetime # Added for output
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
    return {"status": "Code-Review-Service is running"}

@app.post("/", response_model=CodeReviewOut)
def create_code_review_request(review: CodeReviewCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to create code review request for mentor {review.mentor_id} by mentee {review.mentee_id}")
    try:
        db_review = models.CodeReview(
            mentor_id=review.mentor_id,
            mentee_id=review.mentee_id,
            repo_url=str(review.repo_url) # Store as string
            # status and created_at have defaults
        )
        logger.info("Adding review request to session...")
        db.add(db_review)
        logger.info("Committing transaction...")
        db.commit()
        logger.info("Refreshing review object...")
        db.refresh(db_review)
        logger.info(f"Code review request created successfully: {db_review.id}")
        return db_review
    except Exception as e:
        logger.error(f"Error creating code review request: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error creating code review request")

# Add endpoints to get/update reviews later
