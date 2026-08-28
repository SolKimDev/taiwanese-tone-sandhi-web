import logging
import os
import time
from collections import deque
from threading import Lock

from flask import Flask, jsonify, render_template, request

from analyzer import analyze


app = Flask(__name__)
app.logger.setLevel(logging.INFO)


# -------------------------------------------------------------------
# Runtime statistics
#
# 메모리에만 저장한다.
# - Gunicorn/서버 재시작 시 초기화
# - Gunicorn worker마다 별도로 집계
# - 최근 7일의 분석 요청 시각만 보관
# -------------------------------------------------------------------

stats_lock = Lock()
started_at = time.time()

stats = {
    "requests": 0,
    "success": 0,
    "errors": 0,
    "active": 0,
    "total_ms": 0.0,
}

request_times = deque()

# 7 days
REQUEST_HISTORY_SECONDS = 7 * 24 * 60 * 60


def cleanup_request_times(now):
    """최근 7일보다 오래된 요청 기록을 제거한다."""
    cutoff = now - REQUEST_HISTORY_SECONDS

    while request_times and request_times[0] < cutoff:
        request_times.popleft()


def format_uptime(seconds):
    """uptime을 사람이 읽기 쉬운 형태로 변환한다."""
    seconds = int(seconds)

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []

    if days:
        parts.append(f"{days}d")

    if hours or days:
        parts.append(f"{hours}h")

    if minutes or hours or days:
        parts.append(f"{minutes}m")

    parts.append(f"{seconds}s")

    return " ".join(parts)


def get_stats_text():
    """현재 worker의 runtime 통계를 문자열로 만든다."""
    now = time.time()

    with stats_lock:
        cleanup_request_times(now)

        snapshot = stats.copy()
        times = list(request_times)

    uptime = now - started_at

    avg_ms = (
        snapshot["total_ms"] / snapshot["requests"]
        if snapshot["requests"]
        else 0.0
    )

    avg_per_hour = (
        snapshot["requests"] / (uptime / 3600)
        if uptime > 0
        else 0.0
    )

    last_1m = sum(t >= now - 60 for t in times)
    last_10m = sum(t >= now - 600 for t in times)
    last_1h = sum(t >= now - 3600 for t in times)
    last_24h = sum(t >= now - 86400 for t in times)
    last_48h = sum(t >= now - 172800 for t in times)
    last_7d = len(times)

    return (
        "Runtime stats\n"
        f"PID         : {os.getpid()}\n"
        f"Uptime      : {format_uptime(uptime)}\n"
        f"Requests    : {snapshot['requests']}\n"
        f"Success     : {snapshot['success']}\n"
        f"Errors      : {snapshot['errors']}\n"
        f"Active      : {snapshot['active']}\n"
        f"Avg time    : {avg_ms:.1f} ms\n"
        "\n"
        "Recent traffic\n"
        f"Last 1 min  : {last_1m} requests\n"
        f"Last 10 min : {last_10m} requests\n"
        f"Last 1 hour : {last_1h} requests\n"
        f"Last 24 hrs : {last_24h} requests\n"
        f"Last 48 hrs : {last_48h} requests\n"
        f"Last 7 days : {last_7d} requests\n"
        f"Avg/hour    : {avg_per_hour:.1f} requests\n"
    )


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/analyze")
def api_analyze():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify({
            "ok": False,
            "error": "문장을 입력하세요."
        }), 400

    started = time.perf_counter()
    now = time.time()

    with stats_lock:
        stats["requests"] += 1
        stats["active"] += 1

        request_times.append(now)
        cleanup_request_times(now)

    try:
        result = analyze(text)

        with stats_lock:
            stats["success"] += 1

        return jsonify({
            "ok": True,
            "result": result
        })

    except Exception:
        with stats_lock:
            stats["errors"] += 1

        app.logger.exception("Analysis failed")

        return jsonify({
            "ok": False,
            "error": "분석 중 오류가 발생했습니다."
        }), 500

    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000

        with stats_lock:
            stats["active"] -= 1
            stats["total_ms"] += elapsed_ms


@app.post("/internal/log-stats")
def internal_log_stats():
    # Flask에 직접 localhost로 접근한 요청만 허용한다.
    # Nginx에서도 이 경로를 별도로 404 차단한다.
    if request.remote_addr not in ("127.0.0.1", "::1"):
        return "", 404

    text = get_stats_text()

    # journal에도 기록을 남긴다.
    app.logger.info("\n%s", text)

    # curl 한 번으로 바로 확인할 수 있도록 응답에도 출력한다.
    return text, 200, {
        "Content-Type": "text/plain; charset=utf-8"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)