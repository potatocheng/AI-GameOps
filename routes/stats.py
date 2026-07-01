from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db, Feedback
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/overview")
async def get_overview(db: Session = Depends(get_db)):
    try:
        total = db.query(func.count(Feedback.id)).scalar()
        pending = db.query(func.count(Feedback.id)).filter(Feedback.status == "pending").scalar()
        avg_rating = db.query(func.avg(Feedback.rating)).filter(Feedback.rating.isnot(None)).scalar()
        
        return {
            "total_feedback": total,
            "pending_feedback": pending,
            "avg_rating": round(avg_rating, 2) if avg_rating else 0,
            "resolved_rate": round(((total - pending) / total * 100), 2) if total > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback-types")
async def get_feedback_types(db: Session = Depends(get_db)):
    try:
        types = db.query(Feedback.type, func.count(Feedback.id)).group_by(Feedback.type).all()
        return {t[0]: t[1] for t in types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment")
async def get_sentiment_stats(db: Session = Depends(get_db)):
    try:
        sentiment = db.query(Feedback.sentiment, func.count(Feedback.id)).group_by(Feedback.sentiment).all()
        return {s[0]: s[1] for s in sentiment if s[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trend")
async def get_trend(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        trend = db.query(
            func.date(Feedback.created_at),
            func.count(Feedback.id)
        ).filter(Feedback.created_at >= start_date).group_by(func.date(Feedback.created_at)).all()
        
        return {date[0]: date[1] for date in trend}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))