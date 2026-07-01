from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, QAHistory
from pydantic import BaseModel
from typing import Optional, List
from agent.agent import (
    chat_with_agent,
    chat_with_knowledge,
    process_feedback_with_sentiment,
    generate_announcement
)
from agent.knowledge import init_knowledge_base, query_knowledge
from agent.memory import create_memory, get_conversation_summary
import threading

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    player_name: Optional[str] = None
    player_id: Optional[str] = None
    use_knowledge_base: Optional[bool] = True

class AnnouncementGenerateRequest(BaseModel):
    topic: str
    tone: Optional[str] = "friendly"

class FeedbackSentimentRequest(BaseModel):
    content: str

# 知识库初始化标志
_knowledge_base_initialized = False

def init_knowledge_base_async():
    """异步初始化知识库"""
    global _knowledge_base_initialized
    if not _knowledge_base_initialized:
        try:
            init_knowledge_base()
            _knowledge_base_initialized = True
            print("知识库初始化完成")
        except Exception as e:
            print(f"知识库初始化失败: {e}")

# 启动时异步初始化知识库
threading.Thread(target=init_knowledge_base_async, daemon=True).start()

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    与AI运营Agent对话。
    
    使用Agent的自主规划能力，可以调用各种工具完成任务。
    """
    try:
        if request.use_knowledge_base:
            # 使用知识库增强的问答
            result = chat_with_knowledge(request.message)
        else:
            # 使用完整Agent能力
            result = chat_with_agent(request.message, request.session_id)
        
        # 保存问答历史
        try:
            db = next(get_db())
            sentiment_result = process_feedback_with_sentiment(request.message)
            
            qa_history = QAHistory(
                question=request.message,
                answer=result.get("response", ""),
                sentiment=sentiment_result.get("sentiment", "neutral"),
                sentiment_score=sentiment_result.get("sentiment_score", 0.0),
                player_name=request.player_name,
                player_id=request.player_id
            )
            db.add(qa_history)
            db.commit()
        except Exception as e:
            print(f"保存问答历史失败: {e}")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式对话（如果支持）。
    """
    # 目前先返回普通响应
    return await chat(request)

@router.post("/feedback/analyze")
async def analyze_feedback(request: FeedbackSentimentRequest):
    """
    分析反馈内容的情感倾向。
    """
    try:
        result = process_feedback_with_sentiment(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/announcement/generate")
async def create_announcement_content(request: AnnouncementGenerateRequest):
    """
    AI生成游戏公告内容。
    """
    try:
        result = generate_announcement(request.topic, request.tone)
        
        if result.get("success"):
            return {
                "content": result.get("content"),
                "topic": request.topic,
                "tone": request.tone,
                "success": True
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge/search")
async def search_knowledge(query: str, k: int = 3):
    """
    搜索知识库内容。
    """
    try:
        results = query_knowledge(query, k)
        return {"results": results, "query": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{session_id}/summary")
async def get_conversation_history_summary(session_id: str):
    """
    获取对话摘要。
    """
    try:
        summary = get_conversation_summary(session_id)
        return {"session_id": session_id, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation/{session_id}/clear")
async def clear_conversation(session_id: str):
    """
    清除对话记忆。
    """
    try:
        from agent.memory import clear_memory
        success = clear_memory(session_id)
        return {"session_id": session_id, "success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))