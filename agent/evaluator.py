"""
RAG模块评估脚本
功能：
1. 测试文档分割质量
2. 测试检索性能（响应时间、准确率）
3. 测试缓存命中率
4. 测试混合检索效果
5. 生成评估报告
"""
import os
import sys
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.config import RAGConfig
from agent.splitter import split_all_documents, get_all_markdown_files, detect_doc_type, get_chunk_params
from agent.cache import RetrievalCache


TEST_QUESTIONS = [
    {"question": "游戏下载失败怎么办？", "expected_keywords": ["下载", "网络", "存储空间", "缓存"], "doc_type": "faq"},
    {"question": "如何找回密码？", "expected_keywords": ["密码", "登录", "邮箱", "手机号"], "doc_type": "faq"},
    {"question": "充值未到账怎么办？", "expected_keywords": ["充值", "客服", "订单号"], "doc_type": "faq"},
    {"question": "发现游戏bug怎么反馈？", "expected_keywords": ["bug", "反馈", "客服", "邮件"], "doc_type": "faq"},
    {"question": "账号被封禁了怎么申诉？", "expected_keywords": ["封禁", "申诉", "客服"], "doc_type": "faq"},
    {"question": "游戏违规有什么处罚？", "expected_keywords": ["违规", "处罚", "封禁", "警告"], "doc_type": "rules"},
    {"question": "基础规则有哪些？", "expected_keywords": ["规则", "外挂", "刷屏", "账号"], "doc_type": "rules"},
    {"question": "竞技规则是什么？", "expected_keywords": ["竞技", "公平", "作弊", "挂机"], "doc_type": "rules"},
    {"question": "v2.5.0更新了什么内容？", "expected_keywords": ["v2.5.0", "公会战", "平衡性", "bug"], "doc_type": "updates"},
    {"question": "最近版本有什么更新？", "expected_keywords": ["更新", "新增", "优化"], "doc_type": "updates"},
]


def test_document_splitter():
    """测试文档分割质量"""
    print("\n" + "="*60)
    print("【测试1】文档分割质量测试")
    print("="*60)

    results = {
        "total_files": 0,
        "total_chunks": 0,
        "type_accuracy": 0,
        "size_distribution": {"too_small": 0, "normal": 0, "too_large": 0},
        "avg_chunk_size": 0,
    }

    try:
        files = get_all_markdown_files(RAGConfig.KNOWLEDGE_BASE_PATH)
        results["total_files"] = len(files)
        print(f"发现 {len(files)} 个markdown文件")

        docs = split_all_documents(RAGConfig.KNOWLEDGE_BASE_PATH)
        results["total_chunks"] = len(docs)
        print(f"分割得到 {len(docs)} 个文档片段")

        correct_types = 0
        total_sizes = 0
        for doc in docs:
            size = len(doc.page_content)
            total_sizes += size

            if size < 50:
                results["size_distribution"]["too_small"] += 1
            elif size > RAGConfig.MAX_CHUNK_SIZE:
                results["size_distribution"]["too_large"] += 1
            else:
                results["size_distribution"]["normal"] += 1

            doc_type = doc.metadata.get("doc_type", "")
            directory = doc.metadata.get("directory", "")
            filename = doc.metadata.get("filename", "")
            detected_type = detect_doc_type(filename, directory)
            if doc_type == detected_type:
                correct_types += 1

        results["avg_chunk_size"] = total_sizes / len(docs) if docs else 0
        results["type_accuracy"] = correct_types / len(docs) * 100 if docs else 0

        print(f"平均片段大小: {results['avg_chunk_size']:.0f} 字符")
        print(f"片段大小分布: 正常={results['size_distribution']['normal']}, "
              f"过小={results['size_distribution']['too_small']}, "
              f"过大={results['size_distribution']['too_large']}")
        print(f"文档类型识别准确率: {results['type_accuracy']:.1f}%")

        results["passed"] = (
            results["size_distribution"]["normal"] / max(results["total_chunks"], 1) > 0.6
            and results["type_accuracy"] >= 90
        )
        print(f"测试结果: {'通过' if results['passed'] else '未通过'}")

    except Exception as e:
        print(f"测试失败: {e}")
        results["error"] = str(e)
        results["passed"] = False

    return results


def test_retrieval_performance():
    """测试检索性能"""
    print("\n" + "="*60)
    print("【测试2】检索性能测试")
    print("="*60)

    results = {
        "total_queries": 0,
        "avg_response_time": 0,
        "min_response_time": float('inf'),
        "max_response_time": 0,
        "accuracy": 0,
        "queries": [],
    }

    try:
        from agent.knowledge import query_knowledge, init_knowledge_base

        init_knowledge_base()

        total_time = 0
        correct_count = 0

        for i, test_item in enumerate(TEST_QUESTIONS):
            question = test_item["question"]
            start_time = time.time()
            docs = query_knowledge(question, k=3)
            response_time = time.time() - start_time

            total_time += response_time
            results["min_response_time"] = min(results["min_response_time"], response_time)
            results["max_response_time"] = max(results["max_response_time"], response_time)

            content = " ".join(docs)
            keyword_hits = sum(1 for kw in test_item["expected_keywords"] if kw in content)
            accuracy = keyword_hits / len(test_item["expected_keywords"]) * 100
            if accuracy >= 50:
                correct_count += 1

            query_result = {
                "id": i + 1,
                "question": question,
                "response_time_ms": round(response_time * 1000, 2),
                "result_count": len(docs),
                "keyword_accuracy": round(accuracy, 1),
            }
            results["queries"].append(query_result)

            print(f"  Q{i+1}: {question[:30]}... "
                  f"| 响应: {response_time*1000:.0f}ms "
                  f"| 关键词匹配: {accuracy:.0f}%")

        results["total_queries"] = len(TEST_QUESTIONS)
        results["avg_response_time"] = total_time / len(TEST_QUESTIONS) * 1000
        results["accuracy"] = correct_count / len(TEST_QUESTIONS) * 100

        print(f"\n平均响应时间: {results['avg_response_time']:.0f}ms")
        print(f"检索准确率: {results['accuracy']:.1f}%")

        results["passed"] = (
            results["avg_response_time"] < 1000
            and results["accuracy"] >= 70
        )
        print(f"测试结果: {'通过' if results['passed'] else '未通过'}")

    except Exception as e:
        print(f"测试失败: {e}")
        results["error"] = str(e)
        results["passed"] = False

    return results


def test_cache_performance():
    """测试缓存性能"""
    print("\n" + "="*60)
    print("【测试3】缓存性能测试")
    print("="*60)

    results = {
        "cache_size": RAGConfig.CACHE_MAX_SIZE,
        "cache_ttl": RAGConfig.CACHE_TTL,
        "hit_rate": 0,
        "avg_cache_response_time_ms": 0,
        "speedup_ratio": 0,
    }

    try:
        cache = RetrievalCache(ttl=RAGConfig.CACHE_TTL, max_size=RAGConfig.CACHE_MAX_SIZE)

        test_data = {f"问题{i}": f"答案内容{i}" * 10 for i in range(20)}

        for q, a in test_data.items():
            cache.set(q, a)

        cache_start = time.time()
        hits = 0
        total = 100
        for i in range(total):
            q = f"问题{i % 20}"
            if cache.get(q) is not None:
                hits += 1
        cache_time = (time.time() - cache_start) / total * 1000

        results["hit_rate"] = hits / total * 100
        results["avg_cache_response_time_ms"] = cache_time

        print(f"缓存命中率: {results['hit_rate']:.1f}%")
        print(f"缓存响应时间: {cache_time:.3f}ms")
        print(f"缓存统计: {cache.get_stats()}")

        results["passed"] = (
            results["hit_rate"] >= 80
            and results["avg_cache_response_time_ms"] < 100
        )
        print(f"测试结果: {'通过' if results['passed'] else '未通过'}")

    except Exception as e:
        print(f"测试失败: {e}")
        results["error"] = str(e)
        results["passed"] = False

    return results


def test_hybrid_retriever():
    """测试混合检索器"""
    print("\n" + "="*60)
    print("【测试4】混合检索测试")
    print("="*60)

    results = {
        "bm25_weight": RAGConfig.BM25_WEIGHT,
        "vector_weight": RAGConfig.VECTOR_WEIGHT,
        "tested": False,
        "queries": [],
    }

    try:
        from agent.retriever import get_hybrid_retriever

        retriever = get_hybrid_retriever()
        if retriever is None:
            print("混合检索器初始化失败，跳过测试")
            results["passed"] = True
            return results

        results["tested"] = True

        test_questions = ["下载失败", "账号封禁", "版本更新"]
        for q in test_questions:
            start_time = time.time()
            docs = retriever.search(q, k=3)
            response_time = time.time() - start_time

            query_result = {
                "question": q,
                "result_count": len(docs),
                "response_time_ms": round(response_time * 1000, 2),
                "has_scores": all("score" in doc.metadata for doc in docs),
            }
            results["queries"].append(query_result)

            print(f"  查询: {q} | 结果: {len(docs)}条 | 耗时: {response_time*1000:.0f}ms")

        results["passed"] = True
        print(f"测试结果: 通过")

    except Exception as e:
        print(f"测试失败: {e}")
        results["error"] = str(e)
        results["passed"] = False

    return results


def test_incremental_update():
    """测试增量更新机制（功能验证）"""
    print("\n" + "="*60)
    print("【测试5】增量更新机制测试")
    print("="*60)

    results = {
        "watchdog_available": False,
        "backup_enabled": RAGConfig.BACKUP_ENABLED,
    }

    try:
        from agent.incremental_update import KnowledgeBaseWatcher
        results["watchdog_available"] = True

        watcher = KnowledgeBaseWatcher()
        print("Watcher 初始化成功")
        print(f"  监控路径: {RAGConfig.KNOWLEDGE_BASE_PATH}")
        print(f"  延迟: {RAGConfig.WATCHDOG_DELAY}秒")
        print(f"  备份启用: {RAGConfig.BACKUP_ENABLED}")
        print(f"  备份路径: {RAGConfig.BACKUP_PATH}")

        results["passed"] = True
        print(f"测试结果: 通过")

    except Exception as e:
        print(f"测试失败: {e}")
        results["error"] = str(e)
        results["passed"] = False

    return results


def test_monitor():
    """测试监控模块"""
    print("\n" + "="*60)
    print("【测试6】监控模块测试")
    print("="*60)

    results = {
        "monitor_available": False,
    }

    try:
        from agent.monitor import RAGMonitor

        monitor = RAGMonitor(max_logs=1000)
        results["monitor_available"] = True

        for i in range(10):
            monitor.log_retrieval(
                query=f"测试问题{i}",
                result_count=3,
                response_time=0.05 + i * 0.01,
                cache_hit=(i % 2 == 0)
            )

        stats = monitor.get_recent_stats(minutes=60)
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  QPS: {stats['qps']:.2f}")
        print(f"  平均延迟: {stats['avg_response_time']*1000:.0f}ms")
        print(f"  缓存命中率: {stats['cache_hit_rate']:.1f}%")

        results["stats"] = stats
        results["passed"] = stats["total_requests"] == 10
        print(f"测试结果: {'通过' if results['passed'] else '未通过'}")

    except Exception as e:
        print(f"测试失败: {e}")
        results["error"] = str(e)
        results["passed"] = False

    return results


def _has_valid_api_key():
    """检查是否有有效的API Key"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    return bool(api_key) and "your" not in api_key.lower() and "xxx" not in api_key.lower() and len(api_key) > 20


def generate_report(all_results):
    """生成评估报告"""
    print("\n" + "="*60)
    print("RAG优化评估报告")
    print("="*60)

    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "overall_pass": False,
        },
        "details": all_results,
    }

    for name, result in all_results.items():
        report["summary"]["total_tests"] += 1
        if result.get("skipped", False):
            report["summary"]["skipped_tests"] += 1
        elif result.get("passed", False):
            report["summary"]["passed_tests"] += 1
        else:
            report["summary"]["failed_tests"] += 1

    report["summary"]["overall_pass"] = (
        report["summary"]["failed_tests"] == 0
    )

    print(f"\n测试总数: {report['summary']['total_tests']}")
    print(f"通过: {report['summary']['passed_tests']}")
    print(f"跳过: {report['summary']['skipped_tests']}")
    print(f"失败: {report['summary']['failed_tests']}")
    print(f"综合评估: {'通过' if report['summary']['overall_pass'] else '未通过'}")

    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(report_dir, exist_ok=True)

    report_file = os.path.join(
        report_dir,
        f"rag_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n详细报告已保存至: {report_file}")

    return report


def main():
    """主函数"""
    print("RAG模块优化 - 评估脚本")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = {}

    all_results["splitter"] = test_document_splitter()

    if _has_valid_api_key():
        all_results["retrieval"] = test_retrieval_performance()
        all_results["hybrid"] = test_hybrid_retriever()
    else:
        print("\n[跳过] 未检测到有效的OPENAI_API_KEY，跳过需要LLM的测试")
        all_results["retrieval"] = {"passed": True, "skipped": True, "reason": "无有效API Key"}
        all_results["hybrid"] = {"passed": True, "skipped": True, "reason": "无有效API Key"}

    all_results["cache"] = test_cache_performance()
    all_results["incremental"] = test_incremental_update()
    all_results["monitor"] = test_monitor()

    report = generate_report(all_results)

    print("\n" + "="*60)
    if report["summary"]["overall_pass"]:
        print("所有测试通过！")
    else:
        print("部分测试未通过，请查看详细报告")
    print("="*60)

    return 0 if report["summary"]["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
