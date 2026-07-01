from langchain.tools import tool
from sqlalchemy.orm import Session
from database import Feedback, QAHistory, Announcement, SessionLocal
from datetime import datetime, timedelta
from typing import List, Dict, Any

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@tool
def query_feedback(
    keyword: str = "",
    feedback_type: str = "",
    status: str = "",
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    查询玩家反馈，可以按关键词、类型、状态筛选。
    
    Args:
        keyword: 搜索关键词，用于匹配反馈内容
        feedback_type: 反馈类型，可选值: bug, suggestion, complaint, other
        status: 反馈状态，可选值: pending, processing, resolved, closed
        limit: 返回结果数量限制，默认10条
    
    Returns:
        反馈列表，每条反馈包含id, content, type, rating, sentiment, status, priority, created_at
    """
    db = SessionLocal()
    try:
        query = db.query(Feedback)
        
        if keyword:
            query = query.filter(Feedback.content.contains(keyword))
        if feedback_type:
            query = query.filter(Feedback.type == feedback_type)
        if status:
            query = query.filter(Feedback.status == status)
        
        feedbacks = query.order_by(Feedback.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": f.id,
                "content": f.content,
                "type": f.type,
                "rating": f.rating,
                "sentiment": f.sentiment,
                "status": f.status,
                "priority": f.priority,
                "created_at": f.created_at.isoformat()
            }
            for f in feedbacks
        ]
    finally:
        db.close()

@tool
def create_feedback(
    content: str,
    feedback_type: str,
    rating: int = 5,
    player_name: str = "",
    player_id: str = ""
) -> Dict[str, Any]:
    """
    创建新的玩家反馈。
    
    Args:
        content: 反馈内容
        feedback_type: 反馈类型，可选值: bug, suggestion, complaint, other
        rating: 评分，1-5分
        player_name: 玩家名称（可选）
        player_id: 玩家ID（可选）
    
    Returns:
        创建结果，包含id和message
    """
    db = SessionLocal()
    try:
        feedback = Feedback(
            content=content,
            type=feedback_type,
            rating=rating,
            player_name=player_name or None,
            player_id=player_id or None,
            status="pending",
            priority="medium"
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return {"id": feedback.id, "message": "反馈创建成功"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@tool
def update_feedback_status(
    feedback_id: int,
    status: str,
    priority: str = ""
) -> Dict[str, Any]:
    """
    更新反馈状态和优先级。
    
    Args:
        feedback_id: 反馈ID
        status: 新状态，可选值: pending, processing, resolved, closed
        priority: 新优先级，可选值: high, medium, low（可选）
    
    Returns:
        更新结果
    """
    db = SessionLocal()
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            return {"error": "反馈不存在"}
        
        feedback.status = status
        if priority:
            feedback.priority = priority
        feedback.updated_at = datetime.utcnow()
        
        db.commit()
        return {"message": f"反馈 {feedback_id} 状态已更新为 {status}"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@tool
def get_feedback_stats() -> Dict[str, Any]:
    """
    获取反馈统计数据，包括总数、待处理数量、各类型数量、各情感分布。
    
    Returns:
        统计数据字典
    """
    db = SessionLocal()
    try:
        total = db.query(Feedback).count()
        pending = db.query(Feedback).filter(Feedback.status == "pending").count()
        processing = db.query(Feedback).filter(Feedback.status == "processing").count()
        resolved = db.query(Feedback).filter(Feedback.status == "resolved").count()
        
        # 类型分布
        type_counts = {}
        for ftype in ["bug", "suggestion", "complaint", "other"]:
            count = db.query(Feedback).filter(Feedback.type == ftype).count()
            type_counts[ftype] = count
        
        # 情感分布
        sentiment_counts = {}
        for sentiment in ["positive", "neutral", "negative"]:
            count = db.query(Feedback).filter(Feedback.sentiment == sentiment).count()
            sentiment_counts[sentiment] = count
        
        return {
            "total": total,
            "pending": pending,
            "processing": processing,
            "resolved": resolved,
            "type_distribution": type_counts,
            "sentiment_distribution": sentiment_counts
        }
    finally:
        db.close()

@tool
def get_recent_trends(days: int = 7) -> Dict[str, Any]:
    """
    获取最近N天的反馈趋势。
    
    Args:
        days: 天数，默认7天
    
    Returns:
        每日反馈数量统计
    """
    db = SessionLocal()
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        feedbacks = db.query(Feedback).filter(
            Feedback.created_at >= start_date
        ).all()
        
        daily_counts = {}
        for f in feedbacks:
            date_str = f.created_at.strftime("%Y-%m-%d")
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
        
        return {"trends": daily_counts, "days": days}
    finally:
        db.close()

@tool
def save_qa_history(
    question: str,
    answer: str,
    sentiment: str = "",
    sentiment_score: float = 0.0
) -> Dict[str, Any]:
    """
    保存问答历史记录。
    
    Args:
        question: 问题内容
        answer: 回答内容
        sentiment: 情感类型
        sentiment_score: 情感分数
    
    Returns:
        保存结果
    """
    db = SessionLocal()
    try:
        qa = QAHistory(
            question=question,
            answer=answer,
            sentiment=sentiment,
            sentiment_score=sentiment_score
        )
        db.add(qa)
        db.commit()
        db.refresh(qa)
        return {"id": qa.id, "message": "问答历史已保存"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@tool
def create_announcement(title: str, content: str) -> Dict[str, Any]:
    """
    创建游戏公告。
    
    Args:
        title: 公告标题
        content: 公告内容
    
    Returns:
        创建结果
    """
    db = SessionLocal()
    try:
        announcement = Announcement(
            title=title,
            content=content,
            status="draft"
        )
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        return {"id": announcement.id, "message": "公告创建成功"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@tool
def get_announcements(status: str = "") -> List[Dict[str, Any]]:
    """
    获取公告列表。
    
    Args:
        status: 状态筛选，可选值: draft, published（可选）
    
    Returns:
        公告列表
    """
    db = SessionLocal()
    try:
        query = db.query(Announcement)
        if status:
            query = query.filter(Announcement.status == status)
        
        announcements = query.order_by(Announcement.created_at.desc()).all()
        
        return [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "status": a.status,
                "created_at": a.created_at.isoformat()
            }
            for a in announcements
        ]
    finally:
        db.close()

def get_tools():
    """获取所有工具列表"""
    return [
        query_feedback,
        create_feedback,
        update_feedback_status,
        get_feedback_stats,
        get_recent_trends,
        save_qa_history,
        create_announcement,
        get_announcements
    ]