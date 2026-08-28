# -*- coding: utf-8 -*-

import os
import time
from threading import Lock

from flask import Flask, jsonify, render_template, request

from analyzer import analyze


app = Flask(__name__)


# ----------------------------------------------------------------------
# Runtime statistics
#
# 주의:
# - 메모리에만 저장되므로 프로세스가 재시작되면 초기화된다.
# - Gunicorn multi-worker 환경에서는 worker마다 별도의 통계를 가진다.
# - 따라서 전체 서버의 정확한 누적 통계가 아니라 현재 worker의 추정 통계다.
# ----------------------------------------------------------------------

stats_lock = Lock()
started_at = time.time()

stats = {
    "requests": 0,
    "success": 0,
    "errors": 0,
    "active": 0,
    "total_ms": 0.0,
}


def log_stats():
    """현재 worker의 runtime 통계를 애플리케이션 로그에 기록한다."""

    with stats_lock:
        snapshot = stats.copy()

    requests_count = snapshot["requests"]

    avg_ms = (
        snapshot["total_ms"] / requests_count
        if requests_count
        else 0
    )

    uptime = int(time.time() - started_at)

    app.logger.info(
        "STATS pid=%s uptime=%ss requests=%s success=%s errors=%s "
        "active=%s avg_ms=%.1f",
        os.getpid(),
        uptime,
        snapshot["requests"],
        snapshot["success"],
        snapshot["errors"],
        snapshot["active"],
        avg_ms,
    )


# ----------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------

@app.get("/")
def index():
    return render_template("index.html")


# ----------------------------------------------------------------------
# Analysis API
# ----------------------------------------------------------------------

@app.post("/api/analyze")
def api_analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({
            "ok": False,
            "error": "문장을 입력하세요."
        }), 400

    # 너무 큰 요청 방지
    if len(text) > 500:
        return jsonify({
            "ok": False,
            "error": "입력 문장이 너무 깁니다."
        }), 400

    start = time.perf_counter()

    with stats_lock:
        stats["requests"] += 1
        stats["active"] += 1

    try:
        result = analyze(text)

        with stats_lock:
            stats["success"] += 1

    except Exception:
        with stats_lock:
            stats["errors"] += 1

        # 실제 오류 내용은 서버 로그에만 기록한다.
        app.logger.exception("Analysis failed")

        # 사용자에게는 상세 오류를 노출하지 않는다.
        return jsonify({
            "ok": False,
            "error": "분석 중 오류가 발생했습니다."
        }), 500

    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000

        with stats_lock:
            stats["active"] -= 1
            stats["total_ms"] += elapsed_ms

    return jsonify({
        "ok": True,
        "result": result
    })


# ----------------------------------------------------------------------
# Internal runtime statistics
#
# 이 endpoint는 Nginx에서 외부 접근을 반드시 차단한다.
# 서버 내부에서:
#
#   curl -X POST http://127.0.0.1:8000/internal/log-stats
#
# 를 실행하면 현재 worker의 통계가 journal에 기록된다.
# ----------------------------------------------------------------------

@app.post("/internal/log-stats")
def internal_log_stats():
    # Gunicorn에 직접 localhost로 접근하는 경우만 허용한다.
    #
    # 단, Nginx reverse proxy를 거친 외부 요청도 Flask에서는
    # 127.0.0.1로 보일 수 있으므로 이것만으로 보안을 보장하지 않는다.
    # Nginx에서도 해당 경로를 반드시 차단해야 한다.
    if request.remote_addr not in ("127.0.0.1", "::1"):
        return "", 404

    log_stats()

    return "", 204


# ----------------------------------------------------------------------
# Local development
# ----------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)