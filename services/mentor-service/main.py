from fastapi import FastAPI
app = FastAPI(title="SkillBridge - Mentor Service", version="0.1.0")

MENTORS = [
    {"id": 11, "name": "Kasun", "domains": ["backend"], "seniority": "senior", "badges": ["system-design"]},
    {"id": 12, "name": "Nimali", "domains": ["devops"], "seniority": "staff", "badges": ["interview-coach"]},
    {"id": 13, "name": "Ruwan", "domains": ["frontend"], "seniority": "principal", "badges": ["system-design","ui-review"]},
    {"id": 14, "name": "Ishara", "domains": ["data"], "seniority": "senior", "badges": []},
]

@app.get("/health")
def health(): return {"ok": True}

@app.get("/mentors")
def list_mentors(domain: str | None = None, seniority: str | None = None, badge: str | None = None):
    res = MENTORS
    if domain:
        res = [m for m in res if domain in m["domains"]]
    if seniority:
        res = [m for m in res if m["seniority"] == seniority]
    if badge:
        res = [m for m in res if badge in m["badges"]]
    return res
