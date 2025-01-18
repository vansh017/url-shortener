import json
import os
import time
import traceback

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, select, ForeignKey, and_
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime, timedelta
import hashlib
import secrets

# Database setup
DATABASE_URL = "sqlite:///./shortener.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BASE_URL = "https://short.ly/"
HOST = os.getenv("HOST","localhost")
PORT = int(os.getenv("PORT","3500"))

# Models
class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    shortened_url = Column(String, unique=True, nullable=False)
    creation_time = Column(DateTime, default=datetime.utcnow)
    expiration_time = Column(DateTime, nullable=False)
    access_count = Column(Integer, default=0)

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey(URL.id), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=False)

# Pydantic models
class URLRequest(BaseModel):
    original_url: HttpUrl
    expiration_hours: int = 24

class AnalyticsResponse(BaseModel):
    original_url: str
    access_count: int
    access_logs: list

# FastAPI app
app = FastAPI()

Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def get_current_date_time():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def generate_short_url(original_url: str) -> str:
    hash_object = hashlib.md5(original_url.encode())
    short_hash = hash_object.hexdigest()[:6]
    return short_hash

@app.post("/shorten")
def shorten_url(request: URLRequest, db: Session = Depends(get_db)):
    original_url = str(request.original_url)
    short_hash = generate_short_url(original_url)
    shortened_url = BASE_URL + short_hash

    # Check if URL already exists
    current_datetime = get_current_date_time()
    datetime_format = "%Y-%m-%d %H:%M:%S"
    current_datetime = datetime.strptime(current_datetime, datetime_format)
    existing_url = db.query(URL).filter(URL.original_url == str(request.original_url)).first()
    if existing_url:
        return {"shortened_url": existing_url.shortened_url}

    expiration_time = datetime.utcnow() + timedelta(hours=request.expiration_hours)

    # Save URL in the database
    new_url = URL(
        original_url=original_url,
        shortened_url=shortened_url,
        expiration_time=expiration_time,

    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return {"shortened_url": shortened_url}

@app.get("/{short_url}")
def redirect_url(short_url: str, request: Request, db: Session = Depends(get_db)):
    full_url = BASE_URL + short_url

    # Retrieve the URL from the database
    url_entry = db.query(URL).filter(URL.shortened_url == full_url).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Shortened URL not found")

    # Check expiration
    current_datetime = get_current_date_time()
    datetime_format = "%Y-%m-%d %H:%M:%S"
    current_datetime = datetime.strptime(current_datetime, datetime_format)
    if current_datetime > url_entry.expiration_time:
        raise HTTPException(status_code=410, detail="Shortened URL has expired")

    # Log access
    access_log = AccessLog(url_id=url_entry.id, ip_address=request.client.host)
    db.add(access_log)

    # Increment access count
    url_entry.access_count += 1
    db.commit()

    return {"redirect_to": url_entry.original_url}

@app.get("/analytics/{short_url}")
def get_analytics(short_url: str, db: Session = Depends(get_db)):
    full_url = BASE_URL + short_url

    # Retrieve the URL from the database
    url_entry = db.query(URL).filter(URL.shortened_url == full_url).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Shortened URL not found")

    # Retrieve access logs
    access_logs = (db.query(AccessLog)
                   .join(URL, and_(AccessLog.url_id == URL.id)).filter(URL.shortened_url == full_url)
                   .all())
    logs = [{"timestamp": log.timestamp, "ip_address": log.ip_address} for log in access_logs]

    return {
        "original_url": url_entry.original_url,
        "access_count": url_entry.access_count,
        "access_logs": logs
    }
@app.get("/", include_in_schema=False)
def index():
    resp = dict(
        msg="ok",
        jwks_config="/jwks"
    )
    return json.dumps(resp)


if __name__ == "__main__":
    try:
        uvicorn.run("app:app", reload=True, host=HOST, port=PORT)
    except Exception as e:

        traceback.print_exc()

