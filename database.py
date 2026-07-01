from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres123")
POSTGRES_DB = os.getenv("POSTGRES_DB", "game_operator")

DATABASE_URL = f"postgresql+pg8000://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    rating = Column(Integer)
    sentiment = Column(String(20))
    sentiment_score = Column(Float)
    status = Column(String(20), default="pending")
    priority = Column(String(20), default="medium")
    player_name = Column(String(100))
    player_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tags = relationship("FeedbackTag", back_populates="feedback")

class FeedbackTag(Base):
    __tablename__ = "feedback_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedback.id"))
    tag_name = Column(String(50))
    
    feedback = relationship("Feedback", back_populates="tags")

class QAHistory(Base):
    __tablename__ = "qa_history"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    sentiment = Column(String(20))
    sentiment_score = Column(Float)
    player_name = Column(String(100))
    player_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()