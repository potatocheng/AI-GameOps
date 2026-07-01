from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db, Feedback
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

router = APIRouter()

class FeedbackCreate(BaseModel):
    content: str
    type: str
    rating: Optional[int] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    player_name: Optional[str] = None
    player_id: Optional[str] = None

class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None

@router.post("/")
async def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    try:
        db_feedback = Feedback(
            content=feedback.content,
            type=feedback.type,
            rating=feedback.rating,
            sentiment=feedback.sentiment,
            sentiment_score=feedback.sentiment_score,
            player_name=feedback.player_name,
            player_id=feedback.player_id
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return {"id": db_feedback.id, "message": "反馈提交成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_feedback(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Feedback)
        
        if type:
            query = query.filter(Feedback.type == type)
        if status:
            query = query.filter(Feedback.status == status)
        if priority:
            query = query.filter(Feedback.priority == priority)
        if search:
            query = query.filter(Feedback.content.contains(search))
        
        total = query.count()
        feedbacks = query.order_by(Feedback.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
        
        return {
            "data": [
                {
                    "id": f.id,
                    "content": f.content,
                    "type": f.type,
                    "rating": f.rating,
                    "sentiment": f.sentiment,
                    "sentiment_score": f.sentiment_score,
                    "status": f.status,
                    "priority": f.priority,
                    "player_name": f.player_name,
                    "created_at": f.created_at.isoformat()
                } for f in feedbacks
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{feedback_id}")
async def get_feedback_by_id(feedback_id: int, db: Session = Depends(get_db)):
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="反馈不存在")
        return {
            "id": feedback.id,
            "content": feedback.content,
            "type": feedback.type,
            "rating": feedback.rating,
            "sentiment": feedback.sentiment,
            "sentiment_score": feedback.sentiment_score,
            "status": feedback.status,
            "priority": feedback.priority,
            "player_name": feedback.player_name,
            "created_at": feedback.created_at.isoformat(),
            "updated_at": feedback.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{feedback_id}")
async def update_feedback(feedback_id: int, update: FeedbackUpdate, db: Session = Depends(get_db)):
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="反馈不存在")
        
        if update.status:
            feedback.status = update.status
        if update.priority:
            feedback.priority = update.priority
        
        db.commit()
        db.refresh(feedback)
        return {"message": "反馈更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{feedback_id}")
async def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="反馈不存在")
        
        db.delete(feedback)
        db.commit()
        return {"message": "反馈删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))