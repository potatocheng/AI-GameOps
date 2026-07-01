# RAG模块优化 - 文档分割方案设计

## 一、问题分析

当前文档分割方案存在以下问题：

| 问题 | 影响 |
|-----|------|
| 使用 `RecursiveCharacterTextSplitter` | 按字符数机械分割，破坏语义完整性 |
| 不感知文档结构 | Markdown标题层级信息被忽略 |
| 不区分文档类型 | FAQ、规则、更新日志使用相同的分割参数 |
| 元数据不足 | 缺少文档类型、修改时间、来源路径等信息 |
| 不支持递归遍历 | 无法处理子目录中的文档 |

## 二、优化目标

1. **语义完整性**：避免在句子中间或语义相关内容之间截断
2. **结构感知**：充分利用Markdown文档的标题层级结构
3. **差异化处理**：针对不同类型文档使用不同的分割策略
4. **丰富元数据**：记录文档来源、类型、修改时间、标题等信息
5. **递归遍历**：支持知识库目录下的所有子目录

## 三、架构设计

### 3.1 整体流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      文档分割流程                                 │
├─────────────────────────────────────────────────────────────────┤
│  1. 递归遍历目录 ──→ 获取所有 .md 文件列表                        │
│                           ↓                                      │
│  2. 文档类型识别 ──→ 根据文件名前缀/子目录名确定文档类型            │
│                           ↓                                      │
│  3. Markdown结构分割 ──→ 按标题层级（#、##、###）分割              │
│                           ↓                                      │
│  4. 语义感知二次分割 ──→ 对过长片段使用SemanticChunker分割         │
│                           ↓                                      │
│  5. 元数据增强 ──→ 添加来源、类型、标题、修改时间等元数据            │
│                           ↓                                      │
│  6. 返回Document列表 ──→ 供向量数据库存储                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 文件结构

```
agent/
├── splitter.py           # 文档分割器（核心）
├── config.py             # 配置管理
├── knowledge.py          # 知识库主入口（需集成splitter）
└── utils.py              # 工具函数（如文档类型识别）
```

## 四、核心设计

### 4.1 文档类型识别

**优先级规则**：文件名前缀 > 子目录名 > default

| 文档类型 | 文件名前缀 | 子目录名 | 适用场景 |
|---------|-----------|---------|---------|
| `faq` | `faq_*.md` | `/faq/*.md` | 常见问题解答 |
| `rules` | `rules_*.md` | `/rules/*.md` | 游戏规则、条款 |
| `updates` | `updates_*.md` | `/updates/*.md` | 更新日志、公告 |
| `guides` | `guides_*.md` | `/guides/*.md` | 游戏指南、教程 |
| `default` | - | - | 其他类型文档 |

### 4.2 差异化分割参数

| 文档类型 | chunk_size | chunk_overlap | 说明 |
|---------|-----------|---------------|------|
| `faq` | 600 | 100 | Q&A结构清晰，较短chunk即可 |
| `rules` | 1000 | 200 | 规则条款较长，需要更多上下文 |
| `updates` | 800 | 150 | 更新内容中等长度 |
| `guides` | 900 | 150 | 教程内容需要连贯上下文 |
| `default` | 800 | 150 | 默认配置 |

### 4.3 混合分割策略

#### 第一步：Markdown结构分割

使用 `MarkdownHeaderTextSplitter` 按标题层级分割：

```
# 一级标题 ───────────────────────────→ 分割点
内容...

## 二级标题 ────────────────────────→ 分割点
内容...

### 三级标题 ──────────────────────→ 分割点
内容...
```

**优点**：保持文档结构层次，每个片段都有明确的主题

#### 第二步：语义感知二次分割

对第一步分割后的片段，如果长度超过 `chunk_size`，使用 `SemanticChunker` 进行语义分割：

```
计算相邻句子的语义相似度：
├── 句子A ──── 相似度95% ────→ 句子B ──── 相似度45% ────→ 句子C
│                                   ↑
│                              分割点（相似度低于阈值）
└──────────────────────────────────────────────────────────────→
```

**优点**：保持语义相关的内容在同一个chunk中

> **SemanticChunker API注意**：根据实际测试，SemanticChunker 的构造参数为：
> ```python
> SemanticChunker(
>     embeddings,
>     buffer_size=2,
>     breakpoint_threshold_type="percentile",
>     breakpoint_threshold_amount=95,
>     min_chunk_size=200,
>     add_start_index=True
> )
> ```
> 不支持 `max_chunk_size` 参数，对于特别长的文本，需要先用 `RecursiveCharacterTextSplitter` 进行预分割。

### 4.4 元数据设计

每个文档片段包含以下元数据：

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| `source` | string | 相对路径 | `faq/basic.md` |
| `filename` | string | 文件名 | `basic.md` |
| `doc_type` | string | 文档类型 | `faq` |
| `title` | string | 所属章节标题 | `游戏下载与安装` |
| `header_level` | int | 标题层级 | `2` |
| `chunk_index` | int | 在文档中的位置 | `3` |
| `last_modified` | string | 修改时间（ISO格式） | `2024-01-15T10:30:00` |
| `directory` | string | 所属子目录 | `faq` |
| `content_length` | int | 内容长度 | `450` |

### 4.5 目录结构支持

支持以下目录结构：

```
knowledge_base/
├── faq/
│   ├── basic.md
│   ├── payment.md
│   └── account.md
├── rules/
│   ├── game_rules.md
│   └── community_rules.md
├── updates/
│   ├── v2.5.0.md
│   └── v2.5.1.md
├── guides/
│   └── new_player.md
└── misc/
    └── announcement.md
```

## 五、接口设计

### 5.1 `splitter.py`

```python
# 获取所有markdown文件
def get_all_markdown_files(root_dir: str) -> List[dict]:
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

# 识别文档类型
def detect_doc_type(filename: str, dirname: str = "") -> str:
    """
    根据文件名前缀或子目录名识别文档类型
    
    Args:
        filename: 文件名
        dirname: 子目录名（可选）
        
    Returns:
        文档类型: "faq" | "rules" | "updates" | "guides" | "default"
    """

# 获取分割参数
def get_chunk_params(doc_type: str) -> dict:
    """
    获取文档类型对应的chunk参数
    
    Args:
        doc_type: 文档类型
        
    Returns:
        参数字典: {"chunk_size": int, "chunk_overlap": int}
    """

# 分割单个文档
def split_document(file_info: dict) -> List[Document]:
    """
    分割单个文档（混合策略）
    
    Args:
        file_info: 文件信息字典
        
    Returns:
        分割后的Document列表
    """

# 批量分割所有文档
def split_all_documents(root_dir: str = None) -> List[Document]:
    """
    递归遍历目录，分割所有文档
    
    Args:
        root_dir: 根目录路径（默认使用配置中的路径）
        
    Returns:
        所有分割后的Document列表
    """
```

### 5.2 `config.py`

```python
class RAGConfig:
    # 路径配置
    CHROMADB_PATH = "./chroma_db"
    COLLECTION_NAME = "game_knowledge"
    KNOWLEDGE_BASE_PATH = "./knowledge_base"
    
    # Markdown标题层级配置
    MARKDOWN_HEADERS = [
        ("#", "一级标题"),
        ("##", "二级标题"),
        ("###", "三级标题"),
    ]
    
    # 按文档类型配置的chunk参数
    CHUNK_CONFIG = {
        "faq": {"chunk_size": 600, "chunk_overlap": 100},
        "rules": {"chunk_size": 1000, "chunk_overlap": 200},
        "updates": {"chunk_size": 800, "chunk_overlap": 150},
        "guides": {"chunk_size": 900, "chunk_overlap": 150},
        "default": {"chunk_size": 800, "chunk_overlap": 150},
    }
    
    # 语义分割配置
    SEMANTIC_THRESHOLD = 95          # 分割阈值（百分位数）
    MAX_CHUNK_SIZE = 1200            # 最大chunk长度
    MIN_CHUNK_SIZE = 200             # 最小chunk长度
    
    # 检索配置
    RETRIEVAL_K = 5                  # 默认返回文档数
    USE_MMR = True                   # 是否使用MMR多样性检索
    MMR_DIVERSITY = 0.3              # MMR多样性参数
```

## 六、使用示例

```python
# 示例1：获取所有文件
from agent.splitter import get_all_markdown_files

files = get_all_markdown_files("./knowledge_base")
print(f"发现 {len(files)} 个markdown文件")

# 示例2：分割单个文档
from agent.splitter import split_document

file_info = {
    "path": "./knowledge_base/faq/basic.md",
    "rel_path": "faq/basic.md",
    "filename": "basic.md",
    "dir": "faq"
}
docs = split_document(file_info)
print(f"分割结果: {len(docs)}个片段")

# 示例3：批量分割所有文档
from agent.splitter import split_all_documents

all_docs = split_all_documents()
print(f"总片段数: {len(all_docs)}")

# 示例4：集成到knowledge.py
from agent.splitter import split_all_documents
from langchain_chroma import Chroma

all_docs = split_all_documents()
vectordb = Chroma.from_documents(
    documents=all_docs,
    embedding=OpenAIEmbeddings(),
    collection_name="game_knowledge"
)
```

## 七、评估指标

| 指标 | 目标值 | 测量方法 |
|-----|-------|---------|
| 分割后片段长度 | 200-1200字符 | 统计所有片段长度分布 |
| 语义完整性 | 抽查通过率 ≥ 90% | 人工抽查10个片段 |
| 文档类型识别准确率 | ≥ 95% | 测试已知类型文档 |
| 处理1000文档时间 | < 5分钟 | 计时测试 |

## 八、实施计划

| 步骤 | 内容 | 依赖 | 预计时间 |
|-----|------|------|---------|
| 1 | 创建 `config.py` 配置类 | 无 | 30分钟 |
| 2 | 创建 `splitter.py` 核心分割逻辑 | config.py | 2小时 |
| 3 | 修改 `knowledge.py` 集成新分割器 | splitter.py | 1小时 |
| 4 | 测试验证 | 全部 | 1小时 |
| 5 | 文档类型识别测试 | splitter.py | 30分钟 |

## 九、风险与注意事项

1. **SemanticChunker性能**：语义分割需要额外的Embedding调用，可能增加初始化时间（已确认3-4分钟可接受）
2. **中文支持**：需要确保MarkdownHeaderTextSplitter和SemanticChunker对中文文档的支持
3. **大文件处理**：对于特别大的文档，需要确保不会超出内存限制
4. **空文档处理**：需要处理空文件或内容极少的文件，避免产生空片段
5. **编码问题**：需要统一使用UTF-8编码读取文档