from fastapi import FastAPI
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wait for DB (even though this service doesn't use it, wait for consistency)
logger.info("Waiting for database (placeholder)...")
time.sleep(10) # Simple delay

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "WebRTC-Service is running (placeholder)"}

# A real WebRTC service would handle session negotiation (SDP offers/answers, ICE candidates)
@app.post("/signal")
def signal():
    logger.info("Received signal request (placeholder)")
    return {"message": "WebRTC signaling endpoint placeholder"}
