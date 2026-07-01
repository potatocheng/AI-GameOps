from langchain_classic.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./game_operator.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
MemorySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ChatHistoryStore(SQLChatMessageHistory):
    def __init__(self, session_id: str):
        super().__init__(
            session_id=session_id,
            connection_string=DATABASE_URL,
            table_name="chat_history"
        )

def create_memory(session_id: str = "default") -> ConversationBufferMemory:
    """
    创建对话记忆内存。
    
    Args:
        session_id: 会话ID，用于持久化存储对话历史
    
    Returns:
        配置好的ConversationBufferMemory实例
    """
    chat_history = ChatHistoryStore(session_id)
    
    memory = ConversationBufferMemory(
        chat_memory=chat_history,
        memory_key="chat_history",
        output_key="output",
        return_messages=True
    )
    
    return memory

def clear_memory(session_id: str) -> bool:
    """
    清除指定会话的记忆。
    
    Args:
        session_id: 会话ID
    
    Returns:
        是否成功清除
    """
    try:
        chat_history = ChatHistoryStore(session_id)
        chat_history.clear()
        return True
    except Exception as e:
        print(f"清除记忆失败: {e}")
        return False

def get_conversation_summary(session_id: str) -> str:
    """
    获取对话摘要。
    
    Args:
        session_id: 会话ID
    
    Returns:
        对话摘要字符串
    """
    try:
        chat_history = ChatHistoryStore(session_id)
        messages = chat_history.messages
        
        if not messages:
            return "暂无对话历史"
        
        summary_parts = []
        for msg in messages[-10:]:  # 最近10条消息
            if hasattr(msg, 'type'):
                role = "用户" if msg.type == "human" else "AI"
                content = msg.content[:100] if len(msg.content) > 100 else msg.content
                summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)
    except Exception as e:
        return f"获取摘要失败: {str(e)}"