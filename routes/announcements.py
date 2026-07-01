from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Announcement
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    status: Optional[str] = "draft"

@router.post("/")
async def create_announcement(announcement: AnnouncementCreate, db: Session = Depends(get_db)):
    try:
        db_announcement = Announcement(
            title=announcement.title,
            content=announcement.content,
            status=announcement.status
        )
        db.add(db_announcement)
        db.commit()
        db.refresh(db_announcement)
        return {"id": db_announcement.id, "message": "公告创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_announcements(db: Session = Depends(get_db)):
    try:
        announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
        return [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "status": a.status,
                "created_at": a.created_at.isoformat()
            } for a in announcements
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{announcement_id}")
async def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            raise HTTPException(status_code=404, detail="公告不存在")
        return {
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "status": announcement.status,
            "created_at": announcement.created_at.isoformat(),
            "updated_at": announcement.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))