import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from .tools import get_tools
from .memory import create_memory
from .knowledge import get_qa_chain, query_knowledge, init_knowledge_base

load_dotenv()

def create_agent(session_id: str = "default"):
    """
    创建AI运营Agent。
    
    Args:
        session_id: 会话ID，用于管理对话记忆
    
    Returns:
        AgentExecutor实例
    """
    # 获取LLM
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True
    )
    
    # 获取工具
    tools = get_tools()
    
    # 获取提示模板
    prompt = hub.pull("hwchase17/react-chat")
    
    # 创建记忆
    memory = create_memory(session_id)
    
    # 创建Agent
    agent = create_react_agent(llm, tools, prompt)
    
    # 创建Agent执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent_executor

def chat_with_agent(message: str, session_id: str = "default") -> dict:
    """
    与Agent对话。
    
    Args:
        message: 用户消息
        session_id: 会话ID
    
    Returns:
        包含response和intermediate_steps的字典
    """
    try:
        agent_executor = create_agent(session_id)
        
        result = agent_executor.invoke({
            "input": message,
            "chat_history": []
        })
        
        return {
            "response": result.get("output", ""),
            "success": True
        }
    except Exception as e:
        return {
            "response": f"处理您的请求时出错: {str(e)}",
            "success": False,
            "error": str(e)
        }

def chat_with_knowledge(message: str) -> dict:
    """
    基于知识库的问答。
    
    Args:
        message: 用户问题
    
    Returns:
        包含response的字典
    """
    try:
        # 先尝试从知识库检索
        relevant_docs = query_knowledge(message, k=3)
        
        if relevant_docs:
            # 使用知识库增强回答
            qa_chain = get_qa_chain()
            if qa_chain:
                result = qa_chain.invoke({"query": message})
                return {
                    "response": result.get("result", ""),
                    "source": "knowledge_base",
                    "success": True
                }
        
        # 如果知识库没有，使用通用LLM
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        response = llm.invoke(message)
        
        return {
            "response": response.content,
            "source": "llm",
            "success": True
        }
    except Exception as e:
        return {
            "response": f"处理您的问题时出错: {str(e)}",
            "success": False,
            "error": str(e)
        }

def process_feedback_with_sentiment(content: str) -> dict:
    """
    处理反馈并分析情感。
    
    Args:
        content: 反馈内容
    
    Returns:
        包含情感分析结果的字典
    """
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(content)
        
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = "positive"
        elif compound <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "sentiment_score": compound,
            "details": scores,
            "success": True
        }
    except Exception as e:
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "error": str(e),
            "success": False
        }

def generate_announcement(topic: str, tone: str = "friendly") -> dict:
    """
    AI生成游戏公告。
    
    Args:
        topic: 公告主题
        tone: 语气风格，可选值: friendly, official, urgent
    
    Returns:
        生成的公告内容
    """
    try:
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.8,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        tone_instruction = {
            "friendly": "友好、亲切的语气，适当使用表情符号",
            "official": "正式、官方的语气，措辞严谨",
            "urgent": "紧急、重要的语气，强调时间敏感性"
        }
        
        prompt = f"""请为游戏运营生成一篇公告。

主题: {topic}
语气风格: {tone_instruction.get(tone, '友好')}

公告应该包含:
1. 吸引人的标题
2. 主要内容（清晰、有条理）
3. 结束语

请用中文生成公告内容。
"""
        
        response = llm.invoke(prompt)
        
        return {
            "content": response.content,
            "topic": topic,
            "tone": tone,
            "success": True
        }
    except Exception as e:
        return {
            "content": "",
            "error": str(e),
            "success": False
        }