from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from .database import Base
from datetime import datetime

class CodeReview(Base):
    __tablename__ = "code_reviews"
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, index=True)
    mentee_id = Column(Integer, index=True)
    repo_url = Column(String) # Or S3 link if using file uploads
    status = Column(String, default="pending") # e.g., pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow) # --- FIX: Added created_at column ---
