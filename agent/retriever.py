import re
from typing import List, Dict, Tuple, Optional
from langchain_core.documents import Document
from agent.config import RAGConfig
from agent.knowledge import vectordb, init_knowledge_base


def _get_config():
    """
    获取检索配置，包含新增配置项的默认值
    
    Returns:
        配置字典
    """
    return {
        "RETRIEVAL_K": getattr(RAGConfig, "RETRIEVAL_K", 5),
        "USE_MMR": getattr(RAGConfig, "USE_MMR", True),
        "MMR_DIVERSITY": getattr(RAGConfig, "MMR_DIVERSITY", 0.3),
        "BM25_WEIGHT": getattr(RAGConfig, "BM25_WEIGHT", 0.3),
        "VECTOR_WEIGHT": getattr(RAGConfig, "VECTOR_WEIGHT", 0.7),
        "RERANK_ENABLED": getattr(RAGConfig, "RERANK_ENABLED", False),
    }


def _tokenize(text: str) -> List[str]:
    """
    简单的中英文分词
    
    Args:
        text: 输入文本
        
    Returns:
        分词结果列表
    """
    text = text.lower()
    tokens = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z0-9]+', text)
    result = []
    for token in tokens:
        if re.match(r'^[\u4e00-\u9fa5]+$', token):
            result.extend(list(token))
        else:
            result.append(token)
    return result


class BM25Retriever:
    """
    BM25关键词检索器
    基于 rank_bm25 库实现关键词匹配检索
    """
    
    def __init__(self, documents: List[Document]):
        """
        初始化BM25检索器
        
        Args:
            documents: 文档列表
        """
        self.documents = documents
        self.corpus = []
        self.bm25 = None
        self._build_index()
    
    def _build_index(self):
        """构建BM25索引"""
        try:
            from rank_bm25 import BM25Okapi
            
            self.corpus = [_tokenize(doc.page_content) for doc in self.documents]
            self.bm25 = BM25Okapi(self.corpus)
        except ImportError:
            print("警告: rank_bm25 库未安装，BM25检索将不可用")
            self.bm25 = None
    
    def search(self, query: str, k: int = 10) -> List[Tuple[Document, float]]:
        """
        使用BM25检索相关文档
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            (文档, 分数) 元组列表，按分数降序排列
        """
        if self.bm25 is None or not self.documents:
            return []
        
        query_tokens = _tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        
        doc_scores = list(zip(self.documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return doc_scores[:k]


class MMRSearch:
    """
    MMR (Maximal Marginal Relevance) 多样性检索
    在相关性和多样性之间取得平衡
    """
    
    def __init__(self, embedding_function=None):
        """
        初始化MMR检索器
        
        Args:
            embedding_function: 嵌入函数，用于计算向量相似度
        """
        self.embedding_function = embedding_function
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            余弦相似度值
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
    
    def mmr_rerank(
        self,
        query: str,
        documents: List[Document],
        k: int = 5,
        lambda_mult: float = 0.5,
        doc_embeddings: Optional[List[List[float]]] = None,
    ) -> List[Document]:
        """
        使用MMR算法对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 待排序的文档列表
            k: 返回结果数量
            lambda_mult: 多样性参数，0-1之间，越大越看重相关性
            doc_embeddings: 文档向量列表（可选）
            
        Returns:
            重排序后的文档列表
        """
        if not documents:
            return []
        
        if k >= len(documents):
            return documents
        
        if self.embedding_function is None and doc_embeddings is None:
            return documents[:k]
        
        try:
            if doc_embeddings is None:
                query_embedding = self.embedding_function.embed_query(query)
                doc_embeddings = [
                    self.embedding_function.embed_documents([doc.page_content])[0]
                    for doc in documents
                ]
            else:
                query_embedding = self.embedding_function.embed_query(query)
        except Exception as e:
            print(f"MMR嵌入计算失败: {e}")
            return documents[:k]
        
        query_similarities = [
            self._cosine_similarity(query_embedding, doc_emb)
            for doc_emb in doc_embeddings
        ]
        
        selected = []
        selected_indices = []
        candidate_indices = list(range(len(documents)))
        
        for _ in range(min(k, len(documents))):
            best_score = -float('inf')
            best_idx = -1
            
            for idx in candidate_indices:
                relevance = query_similarities[idx]
                
                if not selected:
                    diversity = 0.0
                else:
                    max_sim = max(
                        self._cosine_similarity(doc_embeddings[idx], doc_embeddings[sel_idx])
                        for sel_idx in selected_indices
                    )
                    diversity = max_sim
                
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * diversity
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx
            
            if best_idx == -1:
                break
            
            selected.append(documents[best_idx])
            selected_indices.append(best_idx)
            candidate_indices.remove(best_idx)
        
        return selected


class Reranker:
    """
    结果重排器
    基于交叉编码器或简单规则对检索结果进行重排序
    """
    
    def __init__(self, method: str = "simple"):
        """
        初始化重排器
        
        Args:
            method: 重排方法，目前支持 simple
        """
        self.method = method
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        k: int = 5,
    ) -> List[Document]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 待排序的文档列表
            k: 返回结果数量
            
        Returns:
            重排序后的文档列表
        """
        if not documents or k >= len(documents):
            return documents
        
        if self.method == "simple":
            return self._simple_rerank(query, documents, k)
        
        return documents[:k]
    
    def _simple_rerank(
        self,
        query: str,
        documents: List[Document],
        k: int,
    ) -> List[Document]:
        """
        简单重排：基于关键词匹配度调整分数
        
        Args:
            query: 查询文本
            documents: 待排序的文档列表
            k: 返回结果数量
            
        Returns:
            重排序后的文档列表
        """
        query_tokens = set(_tokenize(query))
        
        scored_docs = []
        for doc in documents:
            content_tokens = set(_tokenize(doc.page_content))
            overlap = len(query_tokens & content_tokens)
            base_score = doc.metadata.get("score", 0.0)
            keyword_boost = overlap / max(len(query_tokens), 1) * 0.1
            final_score = base_score + keyword_boost
            
            new_metadata = dict(doc.metadata)
            new_metadata["score"] = final_score
            new_doc = Document(page_content=doc.page_content, metadata=new_metadata)
            scored_docs.append((new_doc, final_score))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[:k]]


class HybridRetriever:
    """
    混合检索器
    结合 BM25 关键词检索和向量检索，支持MMR多样性和结果重排
    """
    
    def __init__(self):
        """初始化混合检索器"""
        self.config = _get_config()
        self.bm25_retriever = None
        self.mmr_search = MMRSearch()
        self.reranker = Reranker()
        self._all_documents = []
        self._initialized = False
    
    def _ensure_initialized(self):
        """确保检索器已初始化"""
        if self._initialized:
            return
        
        global vectordb
        if vectordb is None:
            init_knowledge_base()
        
        if vectordb is not None:
            try:
                self.mmr_search.embedding_function = vectordb._embedding_function
            except Exception:
                pass
        
        self._load_all_documents()
        self._initialized = True
    
    def _load_all_documents(self):
        """加载所有文档用于BM25检索"""
        global vectordb
        if vectordb is None:
            return
        
        try:
            collection = vectordb._collection
            results = collection.get(include=["documents", "metadatas"])
            
            docs = []
            if results.get("documents") and results.get("metadatas"):
                for content, metadata in zip(results["documents"], results["metadatas"]):
                    docs.append(Document(page_content=content, metadata=metadata or {}))
            
            self._all_documents = docs
            
            if docs:
                self.bm25_retriever = BM25Retriever(docs)
        except Exception as e:
            print(f"加载文档失败: {e}")
            self._all_documents = []
    
    def _vector_search(self, query: str, k: int = 10) -> List[Tuple[Document, float]]:
        """
        向量检索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            (文档, 分数) 元组列表
        """
        global vectordb
        if vectordb is None:
            return []
        
        try:
            docs_with_scores = vectordb.similarity_search_with_score(query, k=k)
            results = []
            for doc, score in docs_with_scores:
                normalized_score = 1.0 / (1.0 + score) if score >= 0 else 0.0
                results.append((doc, normalized_score))
            return results
        except Exception as e:
            print(f"向量检索失败: {e}")
            return []
    
    def _bm25_search(self, query: str, k: int = 10) -> List[Tuple[Document, float]]:
        """
        BM25检索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            (文档, 分数) 元组列表
        """
        if self.bm25_retriever is None:
            if not self._all_documents:
                self._load_all_documents()
            if self.bm25_retriever is None:
                return []
        
        try:
            return self.bm25_retriever.search(query, k=k)
        except Exception as e:
            print(f"BM25检索失败: {e}")
            return []
    
    def _merge_results(
        self,
        bm25_results: List[Tuple[Document, float]],
        vector_results: List[Tuple[Document, float]],
    ) -> List[Document]:
        """
        合并BM25和向量检索结果
        
        Args:
            bm25_results: BM25检索结果
            vector_results: 向量检索结果
            
        Returns:
            合并后的文档列表，metadata中包含分数
        """
        bm25_weight = self.config["BM25_WEIGHT"]
        vector_weight = self.config["VECTOR_WEIGHT"]
        
        doc_scores: Dict[str, Dict] = {}
        
        max_bm25 = max((s for _, s in bm25_results), default=1.0)
        max_vector = max((s for _, s in vector_results), default=1.0)
        
        for doc, score in bm25_results:
            content = doc.page_content
            normalized_score = score / max_bm25 if max_bm25 > 0 else 0.0
            weighted_score = normalized_score * bm25_weight
            
            if content in doc_scores:
                doc_scores[content]["score"] += weighted_score
            else:
                doc_scores[content] = {
                    "doc": doc,
                    "score": weighted_score,
                    "sources": ["bm25"]
                }
        
        for doc, score in vector_results:
            content = doc.page_content
            normalized_score = score / max_vector if max_vector > 0 else 0.0
            weighted_score = normalized_score * vector_weight
            
            if content in doc_scores:
                doc_scores[content]["score"] += weighted_score
                doc_scores[content]["sources"].append("vector")
            else:
                doc_scores[content] = {
                    "doc": doc,
                    "score": weighted_score,
                    "sources": ["vector"]
                }
        
        merged = []
        for content, info in doc_scores.items():
            doc = info["doc"]
            new_metadata = dict(doc.metadata)
            new_metadata["score"] = info["score"]
            new_metadata["retrieval_sources"] = info["sources"]
            if "source" not in new_metadata:
                new_metadata["source"] = new_metadata.get("filename", "unknown")
            if "doc_type" not in new_metadata:
                new_metadata["doc_type"] = new_metadata.get("directory", "default")
            merged.append(Document(page_content=content, metadata=new_metadata))
        
        merged.sort(key=lambda x: x.metadata["score"], reverse=True)
        return merged
    
    def search(
        self,
        query: str,
        k: Optional[int] = None,
        use_mmr: Optional[bool] = None,
        mmr_diversity: Optional[float] = None,
    ) -> List[Document]:
        """
        混合检索主方法
        
        Args:
            query: 查询文本
            k: 返回结果数量，默认使用配置中的RETRIEVAL_K
            use_mmr: 是否使用MMR，默认使用配置中的USE_MMR
            mmr_diversity: MMR多样性参数，默认使用配置中的MMR_DIVERSITY
            
        Returns:
            Document对象列表，page_content为内容，metadata包含score, source, doc_type等
        """
        self._ensure_initialized()
        
        if k is None:
            k = self.config["RETRIEVAL_K"]
        if use_mmr is None:
            use_mmr = self.config["USE_MMR"]
        if mmr_diversity is None:
            mmr_diversity = self.config["MMR_DIVERSITY"]
        
        fetch_k = max(k * 4, 20)
        
        bm25_results = self._bm25_search(query, k=fetch_k)
        vector_results = self._vector_search(query, k=fetch_k)
        
        merged_docs = self._merge_results(bm25_results, vector_results)
        
        if not merged_docs:
            return []
        
        if use_mmr and len(merged_docs) > k:
            merged_docs = self.mmr_search.mmr_rerank(
                query=query,
                documents=merged_docs,
                k=k,
                lambda_mult=mmr_diversity,
            )
        else:
            merged_docs = merged_docs[:k]
        
        if self.config["RERANK_ENABLED"]:
            merged_docs = self.reranker.rerank(query, merged_docs, k=k)
        
        return merged_docs


_default_retriever = None


def get_hybrid_retriever() -> HybridRetriever:
    """
    获取全局混合检索器实例
    
    Returns:
        HybridRetriever实例
    """
    global _default_retriever
    if _default_retriever is None:
        _default_retriever = HybridRetriever()
    return _default_retriever


def hybrid_search(query: str, k: int = None) -> List[Document]:
    """
    便捷函数：执行混合检索
    
    Args:
        query: 查询文本
        k: 返回结果数量
        
    Returns:
        Document对象列表
    """
    retriever = get_hybrid_retriever()
    return retriever.search(query, k=k)
