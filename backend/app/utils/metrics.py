"""
Prometheus 监控指标

功能：
1. QPS 指标
2. 请求延迟
3. 错误计数
4. 自定义业务指标
"""
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    import prometheus_client

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Warning: prometheus-client not installed. Metrics disabled.")

# ========== 指标定义 ==========

if PROMETHEUS_AVAILABLE:
    # HTTP 请求指标
    http_requests_total = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status_code"],
    )

    http_request_duration_seconds = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "endpoint"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
    )

    http_request_size_bytes = Histogram(
        "http_request_size_bytes",
        "HTTP request size in bytes",
        ["method", "endpoint"],
        buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000),
    )

    # NLP 业务指标
    nlp_predictions_total = Counter(
        "nlp_predictions_total",
        "Total NLP predictions",
        ["model_key", "label"],
    )

    nlp_prediction_score = Histogram(
        "nlp_prediction_score",
        "NLP prediction score distribution",
        ["model_key"],
        buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    )

    nlp_prediction_duration_seconds = Histogram(
        "nlp_prediction_duration_seconds",
        "NLP prediction duration in seconds",
        ["model_key"],
        buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
    )

    # 系统指标
    redis_connections_active = Gauge(
        "redis_connections_active",
        "Active Redis connections",
    )

    database_connections_active = Gauge(
        "database_connections_active",
        "Active database connections",
    )

    # 缓存指标
    cache_hits_total = Counter(
        "cache_hits_total",
        "Total cache hits",
        ["cache_type"],
    )

    cache_misses_total = Counter(
        "cache_misses_total",
        "Total cache misses",
        ["cache_type"],
    )


class MetricsMiddleware:
    """Prometheus 指标中间件"""

    def __init__(self):
        if not PROMETHEUS_AVAILABLE:
            raise RuntimeError("prometheus-client not installed")

    async def __call__(self, request, call_next):
        import time

        start_time = time.time()

        # 记录请求大小
        request_size = 0
        if "content-length" in request.headers:
            request_size = int(request.headers["content-length"])

        response = await call_next(request)

        # 计算耗时
        duration = time.time() - start_time

        # 提取端点（简化版本）
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code

        # 记录指标
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        if request_size > 0:
            http_request_size_bytes.labels(
                method=method,
                endpoint=endpoint,
            ).observe(request_size)

        return response


def record_prediction_metrics(model_key: str, label: str, score: float, duration: float):
    """记录预测指标"""
    if not PROMETHEUS_AVAILABLE:
        return

    nlp_predictions_total.labels(
        model_key=model_key,
        label=label,
    ).inc()

    nlp_prediction_score.labels(
        model_key=model_key,
    ).observe(score)

    nlp_prediction_duration_seconds.labels(
        model_key=model_key,
    ).observe(duration)


def record_cache_metrics(cache_type: str, hit: bool):
    """记录缓存指标"""
    if not PROMETHEUS_AVAILABLE:
        return

    if hit:
        cache_hits_total.labels(cache_type=cache_type).inc()
    else:
        cache_misses_total.labels(cache_type=cache_type).inc()


def get_metrics() -> str:
    """获取 Prometheus 格式的指标文本"""
    if not PROMETHEUS_AVAILABLE:
        return "# prometheus-client not installed\n"
    return generate_latest()
