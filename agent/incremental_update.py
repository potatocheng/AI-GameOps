import os
import shutil
import threading
from datetime import datetime
from typing import Dict, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from agent.config import RAGConfig
from agent.splitter import split_document
from agent.knowledge import init_knowledge_base, vectordb, chroma_client
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


class KnowledgeBaseWatcher:
    """
    知识库文件监控与增量更新类。
    
    使用 watchdog 监控知识库目录的文件变化，
    实现向量数据库的增量更新（新增、修改、删除）。
    """

    def __init__(self):
        """初始化监控器"""
        self.knowledge_path = os.path.abspath(RAGConfig.KNOWLEDGE_BASE_PATH)
        self.enabled = RAGConfig.ENABLE_INCREMENTAL_UPDATE
        self.delay = RAGConfig.WATCHDOG_DELAY
        self.backup_enabled = RAGConfig.BACKUP_ENABLED
        self.backup_path = os.path.abspath(RAGConfig.BACKUP_PATH)
        self.chromadb_path = os.path.abspath(RAGConfig.CHROMADB_PATH)
        self.collection_name = RAGConfig.COLLECTION_NAME

        self._observer = None
        self._event_handler = None
        self._file_mtimes: Dict[str, float] = {}
        self._pending_files: Set[str] = set()
        self._lock = threading.Lock()
        self._timer = None
        self._running = False

        self._init_file_mtimes()

    def _init_file_mtimes(self):
        """初始化文件修改时间记录"""
        if not os.path.exists(self.knowledge_path):
            return

        for dirpath, _, filenames in os.walk(self.knowledge_path):
            for filename in filenames:
                if self._is_markdown_file(filename):
                    full_path = os.path.join(dirpath, filename)
                    try:
                        self._file_mtimes[full_path] = os.path.getmtime(full_path)
                    except OSError:
                        pass

    def _is_markdown_file(self, filename: str) -> bool:
        """判断是否为markdown文件"""
        return filename.endswith(".md") and not filename.startswith(".")

    def _get_vectordb(self):
        """获取向量数据库实例"""
        global vectordb, chroma_client
        if vectordb is None or chroma_client is None:
            init_knowledge_base()
        if vectordb is None:
            vectordb = Chroma(
                client=chroma_client,
                collection_name=self.collection_name,
                embedding_function=OpenAIEmbeddings()
            )
        return vectordb

    def _get_collection(self):
        """获取ChromaDB集合"""
        global chroma_client
        if chroma_client is None:
            init_knowledge_base()
        return chroma_client.get_collection(self.collection_name)

    def _backup_vectordb(self):
        """备份向量数据库"""
        if not self.backup_enabled:
            return

        try:
            if not os.path.exists(self.chromadb_path):
                return

            os.makedirs(self.backup_path, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.backup_path, f"backup_{timestamp}")

            shutil.copytree(self.chromadb_path, backup_dir)
            print(f"[增量更新] 向量数据库已备份: {backup_dir}")

            self._cleanup_old_backups()
        except Exception as e:
            print(f"[增量更新] 备份失败: {e}")

    def _cleanup_old_backups(self, keep_count: int = 5):
        """清理旧备份，保留最近N个"""
        try:
            if not os.path.exists(self.backup_path):
                return

            backups = sorted([
                d for d in os.listdir(self.backup_path)
                if d.startswith("backup_") and os.path.isdir(os.path.join(self.backup_path, d))
            ], reverse=True)

            if len(backups) > keep_count:
                for old_backup in backups[keep_count:]:
                    old_path = os.path.join(self.backup_path, old_backup)
                    shutil.rmtree(old_path, ignore_errors=True)
                    print(f"[增量更新] 已清理旧备份: {old_backup}")
        except Exception as e:
            print(f"[增量更新] 清理旧备份失败: {e}")

    def _get_file_info(self, file_path: str) -> dict:
        """构造文件信息字典，供splitter使用"""
        rel_path = os.path.relpath(file_path, self.knowledge_path)
        filename = os.path.basename(file_path)
        parent_dir = os.path.basename(os.path.dirname(file_path))
        if parent_dir == os.path.basename(self.knowledge_path):
            parent_dir = ""

        return {
            "path": file_path,
            "rel_path": rel_path,
            "filename": filename,
            "dir": parent_dir
        }

    def _add_file(self, file_path: str):
        """新增文件：分割并添加到向量数据库"""
        try:
            if not os.path.exists(file_path):
                return

            file_info = self._get_file_info(file_path)
            docs = split_document(file_info)

            if not docs:
                print(f"[增量更新] 文件为空，跳过: {file_info['rel_path']}")
                return

            vectordb = self._get_vectordb()
            vectordb.add_documents(docs)

            self._file_mtimes[file_path] = os.path.getmtime(file_path)
            print(f"[增量更新] 已添加文件: {file_info['rel_path']} ({len(docs)}个片段)")
        except Exception as e:
            print(f"[增量更新] 添加文件失败 {file_path}: {e}")

    def _update_file(self, file_path: str):
        """修改文件：删除旧向量，重新分割添加"""
        try:
            if not os.path.exists(file_path):
                return

            file_info = self._get_file_info(file_path)
            rel_path = file_info["rel_path"]

            collection = self._get_collection()
            try:
                collection.delete(where={"source": rel_path})
            except Exception:
                pass

            docs = split_document(file_info)

            if not docs:
                print(f"[增量更新] 文件为空，已删除旧向量: {rel_path}")
                self._file_mtimes[file_path] = os.path.getmtime(file_path)
                return

            vectordb = self._get_vectordb()
            vectordb.add_documents(docs)

            self._file_mtimes[file_path] = os.path.getmtime(file_path)
            print(f"[增量更新] 已更新文件: {rel_path} ({len(docs)}个片段)")
        except Exception as e:
            print(f"[增量更新] 更新文件失败 {file_path}: {e}")

    def _delete_file(self, file_path: str):
        """删除文件：删除对应向量"""
        try:
            file_info = self._get_file_info(file_path)
            rel_path = file_info["rel_path"]

            collection = self._get_collection()
            try:
                collection.delete(where={"source": rel_path})
            except Exception:
                pass

            if file_path in self._file_mtimes:
                del self._file_mtimes[file_path]

            print(f"[增量更新] 已删除文件: {rel_path}")
        except Exception as e:
            print(f"[增量更新] 删除文件失败 {file_path}: {e}")

    def _process_pending(self):
        """批量处理待处理的文件变更事件"""
        with self._lock:
            if not self._pending_files:
                return

            pending = list(self._pending_files)
            self._pending_files.clear()

        self._backup_vectordb()

        for file_path in pending:
            try:
                if not self._is_markdown_file(os.path.basename(file_path)):
                    continue

                if not os.path.exists(file_path):
                    self._delete_file(file_path)
                    continue

                current_mtime = os.path.getmtime(file_path)
                last_mtime = self._file_mtimes.get(file_path, 0)

                if current_mtime <= last_mtime:
                    continue

                if file_path in self._file_mtimes:
                    self._update_file(file_path)
                else:
                    self._add_file(file_path)
            except Exception as e:
                print(f"[增量更新] 处理文件失败 {file_path}: {e}")

    def _schedule_process(self):
        """调度批量处理（防抖延迟）"""
        if self._timer is not None:
            self._timer.cancel()

        self._timer = threading.Timer(self.delay, self._process_pending)
        self._timer.daemon = True
        self._timer.start()

    def _on_any_event(self, event: FileSystemEvent):
        """统一事件处理入口"""
        if event.is_directory:
            return

        src_path = os.path.abspath(event.src_path)
        if not src_path.startswith(self.knowledge_path):
            return

        if not self._is_markdown_file(os.path.basename(src_path)):
            return

        with self._lock:
            self._pending_files.add(src_path)

            if hasattr(event, 'dest_path') and event.dest_path:
                dest_path = os.path.abspath(event.dest_path)
                self._pending_files.add(dest_path)

        self._schedule_process()

    def start(self):
        """启动文件监控"""
        if not self.enabled:
            print("[增量更新] 增量更新未启用")
            return

        if self._running:
            print("[增量更新] 监控已在运行中")
            return

        os.makedirs(self.knowledge_path, exist_ok=True)

        self._event_handler = _Handler(self._on_any_event)
        self._observer = Observer()
        self._observer.schedule(
            self._event_handler,
            self.knowledge_path,
            recursive=True
        )
        self._observer.start()
        self._running = True
        print(f"[增量更新] 监控已启动: {self.knowledge_path}")

    def stop(self):
        """停止文件监控"""
        if not self._running:
            return

        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None

        self._event_handler = None
        self._running = False
        print("[增量更新] 监控已停止")


class _Handler(FileSystemEventHandler):
    """内部事件处理器，将所有事件转发给回调函数"""

    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def on_created(self, event):
        self._callback(event)

    def on_modified(self, event):
        self._callback(event)

    def on_deleted(self, event):
        self._callback(event)

    def on_moved(self, event):
        self._callback(event)
