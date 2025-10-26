from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from . import models, database
from .database import SessionLocal, engine
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
import time
import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wait for DB to be ready
logger.info("Waiting for database...")
is_db_ready = False
for _ in range(30): # Try for 30 seconds
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
    logger.error("Database connection failed after multiple retries.")

try:
    logger.info("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created (if they didn't exist).")
except Exception as e:
     logger.error(f"Error creating tables: {e}")

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    profile_type: models.ProfileType # Use the enum from models
    # Optional Mentor fields
    seniority: Optional[str] = None
    domains: Optional[str] = None # Expecting comma-separated string from frontend
    badges: Optional[str] = None # Expecting comma-separated string from frontend

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    profile_type: models.ProfileType
    # Optional mentor fields for output
    seniority: Optional[str] = None
    domains: Optional[str] = None
    badges: Optional[str] = None
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
    return {"status": "User-Service is running"}

# Updated GET /mentors to include filtering
@app.get("/mentors", response_model=List[UserOut])
def get_mentors(
    domain: Optional[str] = Query(None, description="Filter by domain (e.g., backend)"),
    seniority: Optional[str] = Query(None, description="Filter by seniority (e.g., senior)"),
    badge: Optional[str] = Query(None, description="Filter by badge (e.g., interview)"),
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching mentors with filters: domain={domain}, seniority={seniority}, badge={badge}")
    try:
        query = db.query(models.User).filter(models.User.profile_type == models.ProfileType.mentor)

        if domain:
            # Assumes domains are stored comma-separated, searches for substring match
            # Use LIKE for partial matching within the comma-separated string
            query = query.filter(models.User.domains.like(f"%{domain}%"))
        if seniority:
            query = query.filter(models.User.seniority == seniority)
        if badge:
             # Assumes badges are stored comma-separated
            query = query.filter(models.User.badges.like(f"%{badge}%"))

        mentors = query.all()
        logger.info(f"Found {len(mentors)} mentors matching filters")
        return mentors
    except Exception as e:
        logger.error(f"Error fetching mentors: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch mentors")


@app.post("/", response_model=UserOut) # Route for user creation
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to create user: {user.email} as {user.profile_type}")
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        logger.info("Hashing password...")
        hashed_password = pwd_context.hash(user.password)
        logger.info("Password hashed.")

        user_data = {
            "email": user.email,
            "hashed_password": hashed_password,
            "profile_type": user.profile_type
        }
        # Add mentor fields if provided and type is mentor
        if user.profile_type == models.ProfileType.mentor:
            if user.seniority: user_data["seniority"] = user.seniority
            # Ensure domains/badges are stored if provided, even if empty string
            user_data["domains"] = user.domains if user.domains is not None else ""
            user_data["badges"] = user.badges if user.badges is not None else ""
            logger.info(f"Creating mentor with details: {user_data}")
        else:
             logger.info(f"Creating mentee: {user_data}")


        db_user = models.User(**user_data)

        logger.info("Adding user to session...")
        db.add(db_user)
        logger.info("Committing transaction...")
        db.commit()
        logger.info("Refreshing user object...")
        db.refresh(db_user)
        logger.info(f"User created successfully: {db_user.id}")
        return db_user
    except HTTPException as http_exc:
        raise http_exc # Re-raise known HTTP exceptions
    except Exception as e:
        logger.error(f"Error creating user {user.email}: {e}")
        db.rollback() # Rollback in case of unexpected error
        raise HTTPException(status_code=500, detail="Internal server error creating user")


@app.post("/login", response_model=UserOut) # Route for login
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Attempting login for: {user_credentials.email}")
    try:
        db_user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

        if not db_user:
            logger.warning(f"Login failed: User not found {user_credentials.email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password") # More generic message

        logger.info("Verifying password...")
        if not pwd_context.verify(user_credentials.password, db_user.hashed_password):
            logger.warning(f"Login failed: Invalid password for {user_credentials.email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        logger.info(f"Login successful for: {user_credentials.email}")
        # In a real app, generate and return a JWT token here
        return db_user # Return user details on successful login

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error during login for {user_credentials.email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during login")

