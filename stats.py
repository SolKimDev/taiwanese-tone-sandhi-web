#!/usr/bin/env python3

import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone


LOG_FILE = "/var/log/nginx/taiwanese-tone-sandhi.access.log"
API_PATH = "/api/analyze"

# 현재 Gunicorn worker 수
EXPECTED_WORKERS = 2

# worker 발견을 위해 internal endpoint를 호출하는 최대 횟수
WORKER_PROBE_ATTEMPTS = 20

# 보안 섹션에서 표시할 suspicious path 최대 개수
MAX_SUSPICIOUS_PATHS = 12

KST = timezone(timedelta(hours=9))


LOG_RE = re.compile(
    r'^\S+ \S+ \S+ '
    r'\[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) [^"]+" '
    r'(?P<status>\d{3}) '
)


def read_log():
    """Nginx access log 전체를 읽는다."""
    try:
        result = subprocess.run(
            ["sudo", "cat", LOG_FILE],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()

    except subprocess.CalledProcessError as exc:
        print("Failed to read Nginx access log.")

        if exc.stderr:
            print(exc.stderr.strip())

        raise SystemExit(1)


def parse_log(lines):
    """
    Nginx 로그를 파싱한다.

    반환:
        [
            {
                "time": datetime,
                "method": str,
                "path": str,
                "status": int,
            },
            ...
        ]
    """
    entries = []

    for line in lines:
        match = LOG_RE.match(line)

        if not match:
            continue

        try:
            timestamp = datetime.strptime(
                match.group("time"),
                "%d/%b/%Y:%H:%M:%S %z",
            )
        except ValueError:
            continue

        # query string은 제거한다.
        path = match.group("path").split("?", 1)[0]

        entries.append(
            {
                "time": timestamp,
                "method": match.group("method"),
                "path": path,
                "status": int(match.group("status")),
            }
        )

    return entries


def filter_api_requests(entries):
    """사용량 통계는 /api/analyze 요청만 사용한다."""
    return [
        entry
        for entry in entries
        if entry["path"] == API_PATH
    ]


def filter_since(entries, cutoff):
    return [
        entry
        for entry in entries
        if entry["time"] >= cutoff
    ]


def get_worker_stats():
    """
    현재 Gunicorn worker별 in-memory 통계를 수집한다.

    internal endpoint는 요청마다 worker 하나가 응답하므로
    여러 번 호출하여 서로 다른 PID를 발견한다.

    특정 worker가 반복 선택될 수 있으므로 모든 worker를
    반드시 발견한다고 보장할 수는 없다.
    """
    workers = {}

    for _ in range(WORKER_PROBE_ATTEMPTS):
        try:
            result = subprocess.run(
                [
                    "curl",
                    "-s",
                    "--max-time",
                    "3",
                    "-X",
                    "POST",
                    "http://127.0.0.1:8000/internal/log-stats",
                ],
                capture_output=True,
                text=True,
            )

        except subprocess.SubprocessError:
            continue

        text = result.stdout

        pid_match = re.search(
            r"^PID\s*:\s*(\d+)",
            text,
            re.MULTILINE,
        )

        req_match = re.search(
            r"^Requests\s*:\s*(\d+)",
            text,
            re.MULTILINE,
        )

        if pid_match and req_match:
            pid = int(pid_match.group(1))
            requests = int(req_match.group(1))

            workers[pid] = requests

        if len(workers) >= EXPECTED_WORKERS:
            break

    return workers


def is_security_event(entry):
    """
    보안 모니터링 대상 응답.

    - 401 Unauthorized
    - 403 Forbidden
    - 404 Not Found
    - 429 Too Many Requests
    - 모든 5xx
    """
    status = entry["status"]

    return (
        status in (401, 403, 404, 429)
        or 500 <= status <= 599
    )


def main():
    now = datetime.now(KST)

    # ---------------------------------------------------------------
    # 전체 Nginx 로그
    # ---------------------------------------------------------------

    entries = parse_log(read_log())

    # ---------------------------------------------------------------
    # Traffic / usage
    #
    # /api/analyze만 집계
    # ---------------------------------------------------------------

    api_entries = filter_api_requests(entries)

    last_1m = filter_since(
        api_entries,
        now - timedelta(minutes=1),
    )

    last_10m = filter_since(
        api_entries,
        now - timedelta(minutes=10),
    )

    last_1h = filter_since(
        api_entries,
        now - timedelta(hours=1),
    )

    last_24h = filter_since(
        api_entries,
        now - timedelta(hours=24),
    )

    last_48h = filter_since(
        api_entries,
        now - timedelta(hours=48),
    )

    last_7d = filter_since(
        api_entries,
        now - timedelta(days=7),
    )

    # ---------------------------------------------------------------
    # /api/analyze response codes
    # ---------------------------------------------------------------

    api_status_classes = Counter(
        entry["status"] // 100
        for entry in last_7d
    )

    # ---------------------------------------------------------------
    # Worker stats
    #
    # Flask process-local memory
    # ---------------------------------------------------------------

    workers = get_worker_stats()

    # ---------------------------------------------------------------
    # Security
    #
    # 여기서는 /api/analyze로 제한하지 않는다.
    # 전체 Nginx 요청을 대상으로 최근 7일을 확인한다.
    # ---------------------------------------------------------------

    all_last_7d = filter_since(
        entries,
        now - timedelta(days=7),
    )

    security_entries = [
        entry
        for entry in all_last_7d
        if is_security_event(entry)
    ]

    security_statuses = Counter(
        entry["status"]
        for entry in security_entries
    )

    security_5xx = sum(
        1
        for entry in security_entries
        if 500 <= entry["status"] <= 599
    )

    suspicious_paths = Counter(
        entry["path"]
        for entry in security_entries
    )

    # ---------------------------------------------------------------
    # Output
    # ---------------------------------------------------------------

    print("Traffic stats")
    print()

    print("Combined")
    print(f"Last 1 min  : {len(last_1m)} requests")
    print(f"Last 10 min : {len(last_10m)} requests")
    print(f"Last 1 hour : {len(last_1h)} requests")
    print(f"Last 24 hrs : {len(last_24h)} requests")
    print(f"Last 48 hrs : {len(last_48h)} requests")
    print(f"Last 7 days : {len(last_7d)} requests")

    print()
    print("Workers (since restart)")

    if workers:
        for pid in sorted(workers):
            print(
                f"PID {pid:<7} : "
                f"{workers[pid]} requests"
            )

        print(
            f"Total       : "
            f"{sum(workers.values())} requests"
        )

        if len(workers) < EXPECTED_WORKERS:
            print(
                f"Warning     : detected "
                f"{len(workers)} of "
                f"{EXPECTED_WORKERS} workers"
            )

    else:
        print("Unavailable")

    print()
    print("Response codes (last 7 days)")
    print(f"2xx         : {api_status_classes[2]}")
    print(f"3xx         : {api_status_classes[3]}")
    print(f"4xx         : {api_status_classes[4]}")
    print(f"5xx         : {api_status_classes[5]}")

    print()
    print("Security events (last 7 days)")
    print(f"401         : {security_statuses[401]}")
    print(f"403         : {security_statuses[403]}")
    print(f"404         : {security_statuses[404]}")
    print(f"429         : {security_statuses[429]}")
    print(f"5xx         : {security_5xx}")

    print()
    print("Top suspicious paths")

    top_paths = suspicious_paths.most_common(
        MAX_SUSPICIOUS_PATHS
    )

    if top_paths:
        width = max(
            len(path)
            for path, _ in top_paths
        )

        # 지나치게 긴 공격 URL 때문에 출력이 망가지지 않도록 제한
        width = min(width, 50)

        for path, count in top_paths:
            if len(path) > 50:
                display_path = path[:47] + "..."
            else:
                display_path = path

            print(
                f"{display_path:<{width}} : "
                f"{count}"
            )

    else:
        print("None")


if __name__ == "__main__":
    main()