from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SkillBridge - User Service", version="0.1.0")

class User(BaseModel):
    id: int
    name: str
    role: str  # 'mentor' or 'mentee'
    headline: str | None = None

DB = [
    {"id": 1, "name": "Sanduni", "role": "mentee", "headline": "Junior Dev"},
    {"id": 2, "name": "Asha", "role": "mentor", "headline": "Senior SRE"}
]

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/users")
def list_users():
    return DB

@app.post("/users")
def create_user(u: User):
    DB.append(u.dict())
    return {"created": u}
