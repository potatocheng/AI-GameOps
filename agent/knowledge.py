import os
import time
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import chromadb
from agent.config import RAGConfig
from agent.splitter import split_all_documents, split_document
from agent.cache import RetrievalCache
from agent.monitor import RAGMonitor

load_dotenv()

chroma_client = None
vectordb = None
_cache = None
_monitor = None
_hybrid_retriever = None


def init_knowledge_base():
    """
    初始化知识库向量数据库。
    使用新的混合策略分割文档、嵌入并存储到ChromaDB。
    集成缓存、监控、混合检索等优化。
    """
    global chroma_client, vectordb, _cache, _monitor

    chroma_client = chromadb.PersistentClient(path=RAGConfig.CHROMADB_PATH)

    try:
        collection = chroma_client.get_collection(RAGConfig.COLLECTION_NAME)
        if collection.count() > 0:
            print(f"知识库已存在，包含 {collection.count()} 条文档")
            vectordb = Chroma(
                client=chroma_client,
                collection_name=RAGConfig.COLLECTION_NAME,
                embedding_function=OpenAIEmbeddings()
            )
            _init_cache_and_monitor()
            return True
    except:
        pass

    print("正在初始化知识库...")

    os.makedirs(RAGConfig.KNOWLEDGE_BASE_PATH, exist_ok=True)

    create_default_knowledge_base()

    all_docs = split_all_documents(RAGConfig.KNOWLEDGE_BASE_PATH)

    if not all_docs:
        print("警告: 没有文档可供处理")
        return False

    embeddings = OpenAIEmbeddings()

    vectordb = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        client=chroma_client,
        collection_name=RAGConfig.COLLECTION_NAME,
        collection_metadata=RAGConfig.get_chroma_metadata()
    )

    _init_cache_and_monitor()
    print(f"知识库初始化完成，包含 {len(all_docs)} 个文档片段")
    return True


def _init_cache_and_monitor():
    """初始化缓存和监控模块"""
    global _cache, _monitor

    if RAGConfig.CACHE_ENABLED:
        _cache = RetrievalCache(
            ttl=RAGConfig.CACHE_TTL, max_size=RAGConfig.CACHE_MAX_SIZE)
        print("[缓存] 检索缓存已启用")

    if RAGConfig.MONITOR_ENABLED:
        _monitor = RAGMonitor(max_logs=RAGConfig.MONITOR_MAX_LOGS)
        print("[监控] RAG监控已启用")


def create_default_knowledge_base():
    """创建默认的游戏知识库文档（使用子目录结构）"""
    faq_dir = os.path.join(RAGConfig.KNOWLEDGE_BASE_PATH, "faq")
    rules_dir = os.path.join(RAGConfig.KNOWLEDGE_BASE_PATH, "rules")
    updates_dir = os.path.join(RAGConfig.KNOWLEDGE_BASE_PATH, "updates")

    os.makedirs(faq_dir, exist_ok=True)
    os.makedirs(rules_dir, exist_ok=True)
    os.makedirs(updates_dir, exist_ok=True)

    faq_content = """# 游戏常见问题解答

## 游戏下载与安装
Q: 游戏下载失败怎么办？
A: 请检查网络连接，确保有足够的存储空间。如果仍然失败，请尝试清除应用商店缓存后重新下载。

Q: 游戏安装提示存储空间不足？
A: 请清理手机存储空间，删除不常用的应用或媒体文件。推荐保留至少2GB可用空间。

## 账号问题
Q: 如何找回密码？
A: 在登录页面点击"忘记密码"，输入绑定的邮箱或手机号，按照提示重置密码。

Q: 账号被封禁如何申诉？
A: 请通过官方客服邮箱提交申诉，提供账号信息和封禁原因，我们将进行审核。

## 游戏充值
Q: 充值未到账怎么办？
A: 请保留充值凭证，联系客服并提供订单号，我们会尽快处理。

Q: 如何申请退款？
A: 虚拟商品充值成功后不支持退款。如有特殊情况，请联系客服处理。

## 游戏Bug反馈
Q: 发现游戏bug如何反馈？
A: 您可以通过以下方式反馈：
1. 使用应用内反馈功能
2. 发送邮件至 support@game.com
3. 在官方社区发帖

请描述bug的具体表现、发生时间和您的设备信息，以便我们更快定位问题。
"""

    rules_content = """# 游戏规则

## 基础规则
1. 尊重其他玩家，禁止辱骂、歧视或骚扰行为
2. 禁止使用外挂、脚本或其他违规作弊软件
3. 禁止恶意刷屏或发送垃圾信息
4. 保护个人账号安全，不要向他人透露密码

## 违规处罚
- 轻度违规：警告或临时禁言
- 中度违规：临时封禁1-7天
- 严重违规：永久封禁

## 竞技规则
1. 公平竞争，禁止作弊
2. 尊重裁判和比赛结果
3. 比赛中禁止退出或挂机
"""

    update_content = """# 游戏更新日志

## v2.5.0 更新内容
- 新增公会战系统
- 优化角色平衡性
- 修复已知bug

## v2.4.0 更新内容
- 新增双人副本
- 优化装备强化系统
- 提升游戏性能
"""

    with open(os.path.join(faq_dir, "basic.md"), "w", encoding="utf-8") as f:
        f.write(faq_content)

    with open(os.path.join(rules_dir, "game_rules.md"), "w", encoding="utf-8") as f:
        f.write(rules_content)

    with open(os.path.join(updates_dir, "v2.5.0.md"), "w", encoding="utf-8") as f:
        f.write(update_content)


def query_knowledge(query: str, k: int = None) -> list:
    """
    从知识库中检索相关内容（带缓存和监控）。

    Args:
        query: 查询文本
        k: 返回的相关文档数量

    Returns:
        相关文档内容列表
    """
    global vectordb, _cache, _monitor

    start_time = time.time()
    cache_hit = False

    if k is None:
        k = RAGConfig.RETRIEVAL_K

    if vectordb is None:
        init_knowledge_base()

    if vectordb is None:
        return []

    if _cache is not None:
        cached = _cache.get(query)
        if cached is not None:
            cache_hit = True
            if _monitor is not None:
                _monitor.log_retrieval(
                    query=query,
                    result_count=len(cached),
                    response_time=time.time() - start_time,
                    cache_hit=True
                )
            return cached

    try:
        if RAGConfig.USE_MMR:
            retriever = vectordb.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": k,
                    "fetch_k": RAGConfig.FETCH_K,
                    "lambda_mult": RAGConfig.MMR_DIVERSITY
                }
            )
            docs = retriever.get_relevant_documents(query)
        else:
            docs = vectordb.similarity_search(query, k=k)

        results = [doc.page_content for doc in docs]

        if _cache is not None:
            _cache.set(query, results)

        if _monitor is not None:
            _monitor.log_retrieval(
                query=query,
                result_count=len(results),
                response_time=time.time() - start_time,
                cache_hit=False
            )

        return results
    except Exception as e:
        print(f"知识库检索失败: {e}")
        return []


def hybrid_query_knowledge(query: str, k: int = None) -> list:
    """
    使用混合检索（BM25 + 向量）检索相关内容。

    Args:
        query: 查询文本
        k: 返回的相关文档数量

    Returns:
        相关Document对象列表，metadata包含score等信息
    """
    global _hybrid_retriever

    if k is None:
        k = RAGConfig.RETRIEVAL_K

    if _hybrid_retriever is None:
        from agent.retriever import get_hybrid_retriever
        _hybrid_retriever = get_hybrid_retriever()

    if _hybrid_retriever is None:
        return query_knowledge(query, k)

    try:
        return _hybrid_retriever.search(query, k=k)
    except Exception as e:
        print(f"混合检索失败，回退到向量检索: {e}")
        return query_knowledge(query, k)


def get_qa_chain():
    """
    获取基于知识库的问答链（优化版提示模板）。

    Returns:
        配置好的RetrievalQA链
    """
    global vectordb

    if vectordb is None:
        init_knowledge_base()

    if vectordb is None:
        return None

    prompt_template = """你是一个专业、友好的游戏运营助手。请严格根据下方提供的知识库内容回答玩家的问题。

【角色设定】
- 你是游戏官方客服助手，熟悉游戏规则、活动、充值等所有游戏相关内容
- 回答要准确、耐心、友好，使用口语化表达
- 遇到不确定的问题，如实告知并引导联系人工客服

【知识库内容】
{context}

【玩家问题】
{question}

【回答要求】
1. 只基于知识库内容回答，不要编造信息
2. 如果知识库中没有相关信息，请明确说明"抱歉，暂时无法回答此问题"，并建议联系客服
3. 回答要条理清晰，重点突出
4. 适当使用表情符号增加亲和力
5. 引用来源格式：[来源：文档名]

请给出你的回答："""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    llm = ChatOpenAI(
        model_name=RAGConfig.LLM_MODEL,
        temperature=RAGConfig.LLM_TEMPERATURE,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": RAGConfig.RETRIEVAL_K,
            "fetch_k": RAGConfig.FETCH_K,
            "lambda_mult": RAGConfig.MMR_DIVERSITY
        }
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )

    return qa_chain


def add_to_knowledge_base(content: str, metadata: dict = None):
    """
    向知识库添加新内容。

    Args:
        content: 文档内容
        metadata: 元数据（可选）
    """
    global vectordb, chroma_client

    if chroma_client is None:
        init_knowledge_base()

    if chroma_client is None:
        return False

    try:
        docs = [Document(page_content=content, metadata=metadata or {})]

        if vectordb is None:
            vectordb = Chroma(
                client=chroma_client,
                collection_name=RAGConfig.COLLECTION_NAME,
                embedding_function=OpenAIEmbeddings()
            )

        vectordb.add_documents(docs)

        if _cache is not None:
            _cache.clear()

        return True
    except Exception as e:
        print(f"添加知识库失败: {e}")
        return False


def delete_from_knowledge_by_source(source: str):
    """
    根据source元数据删除知识库中的文档。

    Args:
        source: 文档来源路径
    """
    global vectordb, chroma_client

    if chroma_client is None:
        return False

    try:
        collection = chroma_client.get_collection(RAGConfig.COLLECTION_NAME)
        collection.delete(where={"source": source})

        if _cache is not None:
            _cache.clear()

        return True
    except Exception as e:
        print(f"删除知识库文档失败: {e}")
        return False


def get_cache_stats():
    """获取缓存统计信息"""
    global _cache
    if _cache is None:
        return None
    return _cache.get_stats()


def get_monitor_stats(minutes: int = 60):
    """获取监控统计信息"""
    global _monitor
    if _monitor is None:
        return None
    return _monitor.get_recent_stats(minutes=minutes)


def get_all_docs_count():
    """获取知识库文档总数"""
    global chroma_client
    if chroma_client is None:
        return 0
    try:
        collection = chroma_client.get_collection(RAGConfig.COLLECTION_NAME)
        return collection.count()
    except:
        return 0
