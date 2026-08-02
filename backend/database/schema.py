from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from database import Base

Base = declarative_base()

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_token = Column(String(255), nullable=False, index=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    vibe_score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
