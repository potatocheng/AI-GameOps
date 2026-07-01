import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import chromadb

load_dotenv()

CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./chroma_db")
KNOWLEDGE_BASE_PATH = "./knowledge_base"

chroma_client = None
vectordb = None

def init_knowledge_base():
    """
    初始化知识库向量数据库。
    加载文档、分割、嵌入并存储到ChromaDB。
    """
    global chroma_client, vectordb
    
    # 创建ChromaDB客户端
    chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
    
    # 检查是否已有集合
    try:
        collection = chroma_client.get_collection("game_knowledge")
        if collection.count() > 0:
            print(f"知识库已存在，包含 {collection.count()} 条文档")
            vectordb = Chroma(
                client=chroma_client,
                collection_name="game_knowledge",
                embedding_function=OpenAIEmbeddings()
            )
            return True
    except:
        pass
    
    # 创建新的知识库
    print("正在初始化知识库...")
    
    # 确保知识库目录存在
    os.makedirs(KNOWLEDGE_BASE_PATH, exist_ok=True)
    
    # 创建默认知识库文档
    create_default_knowledge_base()
    
    # 加载文档
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        os.makedirs(KNOWLEDGE_BASE_PATH, exist_ok=True)
    
    # 加载所有txt和md文件
    loader = DirectoryLoader(
        KNOWLEDGE_BASE_PATH,
        glob="**/*.md",
        loader_cls=TextLoader
    )
    
    try:
        documents = loader.load()
    except Exception as e:
        print(f"加载文档时出错: {e}")
        documents = []
    
    if not documents:
        # 创建默认文档
        create_default_knowledge_base()
        loader = DirectoryLoader(
            KNOWLEDGE_BASE_PATH,
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
    
    # 分割文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    
    texts = text_splitter.split_documents(documents)
    
    if not texts:
        print("警告: 没有文档可供处理")
        return False
    
    # 创建向量存储
    embeddings = OpenAIEmbeddings()
    
    vectordb = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        client=chroma_client,
        collection_name="game_knowledge"
    )
    
    print(f"知识库初始化完成，包含 {len(texts)} 个文档片段")
    return True

def create_default_knowledge_base():
    """创建默认的游戏知识库文档"""
    
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
    
    # 写入文件
    with open(os.path.join(KNOWLEDGE_BASE_PATH, "faq.md"), "w", encoding="utf-8") as f:
        f.write(faq_content)
    
    with open(os.path.join(KNOWLEDGE_BASE_PATH, "rules.md"), "w", encoding="utf-8") as f:
        f.write(rules_content)
    
    with open(os.path.join(KNOWLEDGE_BASE_PATH, "updates.md"), "w", encoding="utf-8") as f:
        f.write(update_content)

def query_knowledge(query: str, k: int = 3) -> list:
    """
    从知识库中检索相关内容。
    
    Args:
        query: 查询文本
        k: 返回的相关文档数量
    
    Returns:
        相关文档列表
    """
    global vectordb
    
    if vectordb is None:
        init_knowledge_base()
    
    if vectordb is None:
        return []
    
    try:
        docs = vectordb.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
    except Exception as e:
        print(f"知识库检索失败: {e}")
        return []

def get_qa_chain():
    """
    获取基于知识库的问答链。
    
    Returns:
        配置好的RetrievalQA链
    """
    global vectordb
    
    if vectordb is None:
        init_knowledge_base()
    
    if vectordb is None:
        return None
    
    # 定义提示模板
    prompt_template = """你是一个友好的游戏运营助手。根据以下知识库内容回答玩家的问题。

知识库内容:
{context}

玩家问题: {question}

请根据知识库内容给出准确、友好的回答。如果知识库中没有相关信息，请说明暂时无法回答，并建议玩家联系客服。
"""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT}
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
        from langchain.schema import Document
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        texts = text_splitter.split_text(content)
        
        documents = [
            Document(page_content=text, metadata=metadata or {}) 
            for text in texts
        ]
        
        if vectordb is None:
            vectordb = Chroma(
                client=chroma_client,
                collection_name="game_knowledge",
                embedding_function=OpenAIEmbeddings()
            )
        
        vectordb.add_documents(documents)
        
        return True
    except Exception as e:
        print(f"添加知识库失败: {e}")
        return False