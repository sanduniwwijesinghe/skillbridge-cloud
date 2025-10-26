from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from .database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, index=True)
    receiver_id = Column(Integer, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
