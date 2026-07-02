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
    FETCH_K = 20
    
    BM25_WEIGHT = 0.3
    VECTOR_WEIGHT = 0.7
    RERANK_ENABLED = False
    
    CHROMA_HNSW_SPACE = "cosine"
    CHROMA_EF_CONSTRUCTION = 256
    CHROMA_EF_SEARCH = 128
    CHROMA_M = 16
    
    ENABLE_INCREMENTAL_UPDATE = True
    WATCHDOG_DELAY = 5
    BACKUP_ENABLED = True
    BACKUP_PATH = "./chroma_db_backups"
    BACKUP_KEEP_COUNT = 5
    
    CACHE_ENABLED = True
    CACHE_TTL = 300
    CACHE_MAX_SIZE = 1000
    
    MONITOR_ENABLED = True
    MONITOR_MAX_LOGS = 10000
    
    LLM_MODEL = "gpt-3.5-turbo"
    LLM_TEMPERATURE = 0.7
    
    @classmethod
    def get_chroma_metadata(cls):
        return {
            "hnsw:space": cls.CHROMA_HNSW_SPACE,
            "hnsw:construction_ef": cls.CHROMA_EF_CONSTRUCTION,
            "hnsw:search_ef": cls.CHROMA_EF_SEARCH,
            "hnsw:M": cls.CHROMA_M,
        }