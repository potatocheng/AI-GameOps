import hashlib
import time
from collections import OrderedDict


class RetrievalCache:
    """
    检索结果缓存类，实现基于LRU策略的缓存管理。
    
    支持基于问题文本哈希的缓存键、缓存过期时间、LRU淘汰策略，
    以及缓存命中率统计。
    """

    def __init__(self, max_size: int = 1000, ttl: int = 300):
        """
        初始化检索缓存。
        
        Args:
            max_size: 最大缓存条目数，默认1000
            ttl: 缓存过期时间（秒），默认300秒
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache = OrderedDict()
        self._hit_count = 0
        self._miss_count = 0

    def _make_key(self, query: str) -> str:
        """
        根据查询文本生成缓存键（MD5哈希）。
        
        Args:
            query: 查询文本
            
        Returns:
            哈希后的缓存键字符串
        """
        return hashlib.md5(query.encode('utf-8')).hexdigest()

    def get(self, query: str):
        """
        从缓存中获取检索结果。
        
        Args:
            query: 查询文本
            
        Returns:
            缓存的检索结果，如果不存在或已过期则返回None
        """
        key = self._make_key(query)

        if key not in self._cache:
            self._miss_count += 1
            return None

        entry = self._cache[key]
        current_time = time.time()

        if current_time - entry['timestamp'] > self.ttl:
            del self._cache[key]
            self._miss_count += 1
            return None

        self._cache.move_to_end(key)
        self._hit_count += 1
        return entry['data']

    def set(self, query: str, data) -> None:
        """
        将检索结果存入缓存。
        
        Args:
            query: 查询文本
            data: 检索结果数据
        """
        key = self._make_key(query)
        current_time = time.time()

        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = {
                'data': data,
                'timestamp': current_time
            }
            return

        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = {
            'data': data,
            'timestamp': current_time
        }

    def clear(self) -> None:
        """
        清空所有缓存，并重置统计数据。
        """
        self._cache.clear()
        self._hit_count = 0
        self._miss_count = 0

    def get_stats(self) -> dict:
        """
        获取缓存统计信息。
        
        Returns:
            包含命中率、命中次数、未命中次数、当前缓存大小的字典
        """
        total = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total * 100) if total > 0 else 0.0

        return {
            'hit_count': self._hit_count,
            'miss_count': self._miss_count,
            'total_requests': total,
            'hit_rate': round(hit_rate, 2),
            'current_size': len(self._cache),
            'max_size': self.max_size,
            'ttl': self.ttl
        }
