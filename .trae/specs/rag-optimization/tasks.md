# RAG模块优化 - Implementation Plan

## [x] Task 1: 文档分割策略优化（混合策略）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `config.py` 配置类，集中管理所有参数
  - 创建 `splitter.py` 核心分割模块：
    - `get_all_markdown_files`: 递归遍历目录获取所有.md文件
    - `detect_doc_type`: 根据文件名前缀/子目录名识别文档类型（faq/rules/updates/guides/default）
    - `get_chunk_params`: 获取文档类型对应的chunk参数
    - `split_document`: 混合策略分割单个文档（Markdown结构分割 + 语义感知二次分割）
    - `split_all_documents`: 批量分割所有文档
  - 支持的文档类型及参数：
    - faq: chunk_size=600, chunk_overlap=100
    - rules: chunk_size=1000, chunk_overlap=200
    - updates: chunk_size=800, chunk_overlap=150
    - guides: chunk_size=900, chunk_overlap=150
    - default: chunk_size=800, chunk_overlap=150
  - 丰富的元数据：source, filename, doc_type, title, header_level, chunk_index, last_modified, directory, content_length
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 分割后的文档片段长度在200-1200字符之间
  - `programmatic` TR-1.2: 文档类型识别准确率 ≥ 95%
  - `human-judgment` TR-1.3: 抽查10个文档片段，确保语义完整性
- **Notes**: 需要安装langchain-experimental包；支持递归遍历子目录；支持文件名前缀和子目录名两种识别方式

## [ ] Task 2: 检索策略优化（混合检索+MMR）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 实现混合检索：关键词检索（BM25）+ 向量检索（Embeddings）
  - 配置MMR（Maximum Marginal Relevance）多样性检索
  - 添加检索结果重排（Rerank）功能
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: 混合检索结果包含关键词匹配和语义相关的文档
  - `programmatic` TR-2.2: MMR检索结果多样性评分 >= 0.7
- **Notes**: 需要安装langchain-community和rank_bm25包

## [ ] Task 3: 向量数据库优化
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 配置ChromaDB集合参数（hnsw_space、ef_construction等）
  - 优化向量索引构建策略
  - 实现向量数据库连接池和复用机制
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 单次检索响应时间 < 1秒
  - `programmatic` TR-3.2: 并发10次检索平均响应时间 < 1.5秒
- **Notes**: ChromaDB的HNSW索引参数对性能影响较大

## [ ] Task 4: 提示模板优化
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 设计结构化的提示模板，包含角色定义、检索结果格式、回答要求
  - 实现上下文筛选机制，只保留最相关的信息
  - 添加检索结果来源标注
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgment` TR-4.1: 回答内容准确引用知识库信息
  - `human-judgment` TR-4.2: 回答格式清晰，来源可追溯
- **Notes**: 提示模板设计需要结合游戏运营场景

## [ ] Task 5: 增量更新机制与文件Watcher
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 实现文件系统Watcher（watchdog库）监控知识库目录变化
  - 实现增量更新逻辑：检测新增/修改/删除的文件
  - 实现向量数据库备份机制（更新前自动备份）
  - 按文件修改时间对比实现增量更新，只处理变更的文件
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 修改文件后，Watcher在5秒内触发增量更新
  - `programmatic` TR-5.2: 更新前自动创建备份文件
  - `programmatic` TR-5.3: 增量更新后，向量数据库包含最新文档内容
- **Notes**: 文档类型通过文件名前缀识别；不需要保留文档历史版本

## [ ] Task 6: 缓存机制实现
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 实现检索结果缓存（基于问题哈希）
  - 设置合理的缓存过期时间
  - 添加缓存命中率统计
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 相同问题重复检索时，缓存命中率 >= 80%
  - `programmatic` TR-6.2: 缓存响应时间 < 100ms
- **Notes**: 使用functools.lru_cache或Redis

## [ ] Task 7: 评估指标体系构建
- **Priority**: medium
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 编写评估脚本，包含测试问题集合
  - 实现检索准确率计算（基于相关性标注）
  - 实现响应时间测量
  - 生成优化前后对比报告
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 评估脚本能够输出结构化的性能报告
  - `programmatic` TR-7.2: 能够计算并对比优化前后的各项指标
- **Notes**: 需要创建测试数据集

## [ ] Task 8: RAG监控与可观测性
- **Priority**: low
- **Depends On**: Task 2, Task 5
- **Description**: 
  - 添加检索日志记录（查询文本、检索结果、响应时间）
  - 实现性能指标采集（QPS、延迟、命中率）
  - 创建监控仪表盘数据接口
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 系统能够记录每次检索的详细日志
  - `programmatic` TR-8.2: 能够查询最近1小时的检索统计数据
- **Notes**: 可以集成Prometheus或使用简单的日志分析