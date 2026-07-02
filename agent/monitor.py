import time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RetrievalLog:
    """
    检索日志数据类。
    
    记录单次检索的详细信息。
    """
    query: str
    result_count: int
    response_time: float
    cache_hit: bool
    timestamp: float = field(default_factory=time.time)


class RAGMonitor:
    """
    RAG监控与可观测性类。
    
    记录每次检索的详细日志，采集性能指标（QPS、平均延迟、缓存命中率），
    提供统计数据查询功能。
    """

    def __init__(self, max_logs: int = 10000):
        """
        初始化RAG监控器。
        
        Args:
            max_logs: 最大保留日志数量，默认10000条
        """
        self._logs: deque = deque(maxlen=max_logs)

    def log_retrieval(self, query: str, result_count: int, response_time: float, cache_hit: bool) -> None:
        """
        记录一次检索操作。
        
        Args:
            query: 查询文本
            result_count: 检索结果数量
            response_time: 响应时间（秒）
            cache_hit: 是否命中缓存
        """
        log_entry = RetrievalLog(
            query=query,
            result_count=result_count,
            response_time=response_time,
            cache_hit=cache_hit
        )
        self._logs.append(log_entry)

    def get_recent_stats(self, minutes: int = 60) -> dict:
        """
        获取最近指定时间内的统计数据。
        
        Args:
            minutes: 统计时间范围（分钟），默认60分钟
            
        Returns:
            包含QPS、平均延迟、缓存命中率等指标的统计字典
        """
        current_time = time.time()
        time_threshold = current_time - (minutes * 60)

        recent_logs = [
            log for log in self._logs
            if log.timestamp >= time_threshold
        ]

        total_count = len(recent_logs)
        time_span = minutes * 60

        if total_count == 0:
            return {
                'time_window_minutes': minutes,
                'total_requests': 0,
                'qps': 0.0,
                'avg_response_time': 0.0,
                'min_response_time': 0.0,
                'max_response_time': 0.0,
                'cache_hit_count': 0,
                'cache_miss_count': 0,
                'cache_hit_rate': 0.0,
                'total_results': 0,
                'avg_result_count': 0.0
            }

        cache_hit_count = sum(1 for log in recent_logs if log.cache_hit)
        cache_miss_count = total_count - cache_hit_count
        total_response_time = sum(log.response_time for log in recent_logs)
        total_results = sum(log.result_count for log in recent_logs)

        qps = total_count / time_span
        avg_response_time = total_response_time / total_count
        min_response_time = min(log.response_time for log in recent_logs)
        max_response_time = max(log.response_time for log in recent_logs)
        cache_hit_rate = (cache_hit_count / total_count * 100) if total_count > 0 else 0.0
        avg_result_count = total_results / total_count

        return {
            'time_window_minutes': minutes,
            'total_requests': total_count,
            'qps': round(qps, 4),
            'avg_response_time': round(avg_response_time, 4),
            'min_response_time': round(min_response_time, 4),
            'max_response_time': round(max_response_time, 4),
            'cache_hit_count': cache_hit_count,
            'cache_miss_count': cache_miss_count,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'total_results': total_results,
            'avg_result_count': round(avg_result_count, 2)
        }

    def get_all_stats(self) -> dict:
        """
        获取所有历史数据的统计信息。
        
        Returns:
            包含全部日志统计指标的字典
        """
        total_count = len(self._logs)

        if total_count == 0:
            return {
                'total_requests': 0,
                'cache_hit_count': 0,
                'cache_miss_count': 0,
                'cache_hit_rate': 0.0,
                'avg_response_time': 0.0,
                'total_results': 0,
                'avg_result_count': 0.0
            }

        cache_hit_count = sum(1 for log in self._logs if log.cache_hit)
        total_response_time = sum(log.response_time for log in self._logs)
        total_results = sum(log.result_count for log in self._logs)

        return {
            'total_requests': total_count,
            'cache_hit_count': cache_hit_count,
            'cache_miss_count': total_count - cache_hit_count,
            'cache_hit_rate': round(cache_hit_count / total_count * 100, 2),
            'avg_response_time': round(total_response_time / total_count, 4),
            'total_results': total_results,
            'avg_result_count': round(total_results / total_count, 2)
        }

    def get_recent_logs(self, limit: int = 100) -> List[dict]:
        """
        获取最近的检索日志。
        
        Args:
            limit: 返回日志数量上限，默认100条
            
        Returns:
            检索日志字典列表
        """
        recent_logs = list(self._logs)[-limit:]
        return [
            {
                'query': log.query,
                'result_count': log.result_count,
                'response_time': round(log.response_time, 4),
                'cache_hit': log.cache_hit,
                'timestamp': log.timestamp
            }
            for log in reversed(recent_logs)
        ]
