from sqlalchemy import Column, Integer, String, Enum
from .database import Base
import enum

class ProfileType(str, enum.Enum):
    mentee = "mentee"
    mentor = "mentor"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_type = Column(Enum(ProfileType), default=ProfileType.mentee, nullable=False)
    # Mentor specific fields (nullable means they are optional)
    seniority = Column(String, nullable=True) # e.g., 'senior', 'staff', 'principal'
    domains = Column(String, nullable=True) # Comma-separated e.g., 'backend,frontend'
    badges = Column(String, nullable=True) # Comma-separated e.g., 'interview,system-design'
