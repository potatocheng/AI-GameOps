import os
from dotenv import load_dotenv

load_dotenv()

class RAGConfig:
    CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./chroma_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "game_knowledge")
    KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base")
    
    MARKDOWN_HEADERS = [
        ("#", "一级标题"),
        ("##", "二级标题"),
        ("###", "三级标题"),
    ]
    
    CHUNK_CONFIG = {
        "faq": {"chunk_size": 600, "chunk_overlap": 100},
        "rules": {"chunk_size": 1000, "chunk_overlap": 200},
        "updates": {"chunk_size": 800, "chunk_overlap": 150},
        "guides": {"chunk_size": 900, "chunk_overlap": 150},
        "default": {"chunk_size": 800, "chunk_overlap": 150},
    }
    
    SEMANTIC_THRESHOLD = 95
    MAX_CHUNK_SIZE = 1200
    MIN_CHUNK_SIZE = 200
    
    RETRIEVAL_K = 5
    USE_MMR = True
    MMR_DIVERSITY = 0.3
    
    ENABLE_INCREMENTAL_UPDATE = True
    WATCHDOG_DELAY = 5
    BACKUP_ENABLED = True
    BACKUP_PATH = "./chroma_db_backups"