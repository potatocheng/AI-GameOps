import os
from typing import List, Dict
from datetime import datetime
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from agent.config import RAGConfig

def get_all_markdown_files(root_dir: str) -> List[Dict]:
    """
    递归遍历目录，获取所有markdown文件
    
    Args:
        root_dir: 根目录路径
        
    Returns:
        文件信息列表: [
            {
                "path": "/full/path/to/file.md",
                "rel_path": "subdir/file.md",
                "filename": "file.md",
                "dir": "subdir"
            }
        ]
    """
    md_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".md") and not filename.startswith("."):
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)
                parent_dir = os.path.basename(dirpath)
                if parent_dir == os.path.basename(root_dir):
                    parent_dir = ""
                
                md_files.append({
                    "path": full_path,
                    "rel_path": rel_path,
                    "filename": filename,
                    "dir": parent_dir
                })
    
    print(f"发现 {len(md_files)} 个markdown文件")
    return md_files

def detect_doc_type(filename: str, dirname: str = "") -> str:
    """
    根据文件名前缀或子目录名识别文档类型
    优先级: 文件名前缀 > 子目录名 > default
    
    Args:
        filename: 文件名
        dirname: 子目录名（可选）
        
    Returns:
        文档类型: "faq" | "rules" | "updates" | "guides" | "default"
    """
    name = filename.lower()
    
    if name.startswith("faq_"):
        return "faq"
    elif name.startswith("rules_"):
        return "rules"
    elif name.startswith("updates_"):
        return "updates"
    elif name.startswith("guides_"):
        return "guides"
    
    if dirname:
        dir_lower = dirname.lower()
        if dir_lower == "faq":
            return "faq"
        elif dir_lower == "rules":
            return "rules"
        elif dir_lower == "updates":
            return "updates"
        elif dir_lower == "guides":
            return "guides"
    
    return "default"

def get_chunk_params(doc_type: str) -> Dict:
    """
    获取文档类型对应的chunk参数
    
    Args:
        doc_type: 文档类型
        
    Returns:
        参数字典: {"chunk_size": int, "chunk_overlap": int}
    """
    return RAGConfig.CHUNK_CONFIG.get(doc_type, RAGConfig.CHUNK_CONFIG["default"])

def _extract_header_level(metadata: Dict) -> int:
    """从metadata中提取标题层级"""
    if "三级标题" in metadata:
        return 3
    elif "二级标题" in metadata:
        return 2
    elif "一级标题" in metadata:
        return 1
    return 2

def _extract_title(metadata: Dict, filename: str) -> str:
    """从metadata中提取标题"""
    return metadata.get("三级标题") or metadata.get("二级标题") or metadata.get("一级标题") or filename

def split_document(file_info: Dict) -> List[Document]:
    """
    分割单个文档（混合策略）
    
    步骤:
    1. 使用MarkdownHeaderTextSplitter按标题结构分割
    2. 对过长的片段使用RecursiveCharacterTextSplitter预分割
    3. 使用SemanticChunker进行语义感知分割
    
    Args:
        file_info: 文件信息字典
        
    Returns:
        分割后的Document列表
    """
    file_path = file_info["path"]
    filename = file_info["filename"]
    rel_path = file_info["rel_path"]
    dirname = file_info["dir"]
    
    doc_type = detect_doc_type(filename, dirname)
    chunk_params = get_chunk_params(doc_type)
    
    last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if not content.strip():
        return []
    
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=RAGConfig.MARKDOWN_HEADERS,
        strip_headers=False
    )
    
    md_docs = markdown_splitter.split_text(content)
    
    embeddings = OpenAIEmbeddings()
    semantic_splitter = SemanticChunker(
        embeddings,
        buffer_size=2,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=RAGConfig.SEMANTIC_THRESHOLD,
        min_chunk_size=RAGConfig.MIN_CHUNK_SIZE,
        add_start_index=True
    )
    
    pre_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_params["chunk_size"] * 2,
        chunk_overlap=chunk_params["chunk_overlap"],
        length_function=len
    )
    
    final_docs = []
    chunk_index = 0
    
    for md_doc in md_docs:
        content_length = len(md_doc.page_content)
        
        if content_length > chunk_params["chunk_size"]:
            if content_length > RAGConfig.MAX_CHUNK_SIZE * 2:
                pre_chunks = pre_splitter.split_text(md_doc.page_content)
            else:
                pre_chunks = [md_doc.page_content]
            
            for pre_chunk in pre_chunks:
                if len(pre_chunk) < RAGConfig.MIN_CHUNK_SIZE:
                    semantic_chunks = [pre_chunk]
                else:
                    semantic_chunks = semantic_splitter.split_text(pre_chunk)
                
                for chunk in semantic_chunks:
                    title = _extract_title(md_doc.metadata, filename)
                    header_level = _extract_header_level(md_doc.metadata)
                    
                    metadata = {
                        "source": rel_path,
                        "filename": filename,
                        "doc_type": doc_type,
                        "title": title,
                        "header_level": header_level,
                        "chunk_index": chunk_index,
                        "last_modified": last_modified.isoformat(),
                        "directory": dirname,
                        "content_length": len(chunk)
                    }
                    final_docs.append(Document(page_content=chunk, metadata=metadata))
                    chunk_index += 1
        else:
            title = _extract_title(md_doc.metadata, filename)
            header_level = _extract_header_level(md_doc.metadata)
            
            md_doc.metadata.update({
                "source": rel_path,
                "filename": filename,
                "doc_type": doc_type,
                "title": title,
                "header_level": header_level,
                "chunk_index": chunk_index,
                "last_modified": last_modified.isoformat(),
                "directory": dirname,
                "content_length": len(md_doc.page_content)
            })
            final_docs.append(md_doc)
            chunk_index += 1
    
    return final_docs

def split_all_documents(root_dir: str = None) -> List[Document]:
    """
    递归遍历目录，分割所有文档
    
    Args:
        root_dir: 根目录路径（默认使用配置中的路径）
        
    Returns:
        所有分割后的Document列表
    """
    if root_dir is None:
        root_dir = RAGConfig.KNOWLEDGE_BASE_PATH
    
    os.makedirs(root_dir, exist_ok=True)
    
    all_files = get_all_markdown_files(root_dir)
    all_docs = []
    
    for file_info in all_files:
        try:
            docs = split_document(file_info)
            all_docs.extend(docs)
            print(f"分割完成: {file_info['rel_path']} -> {len(docs)}个片段")
        except Exception as e:
            print(f"分割失败: {file_info['rel_path']} - {e}")
    
    print(f"\n全部分割完成，共 {len(all_docs)} 个文档片段")
    return all_docs