"""
Демонстрация rate limiting Nginx: много параллельных запросов к /generate.
Запускайте при работающем стеке: docker compose up (порт 80) или укажите --url.

Ожидаемо: часть ответов 200 (JSON), часть 503 — срабатывает limit_req (2 r/s, burst 5).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import sys
import urllib.error
import urllib.request


def one_request(url: str, timeout: float) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.reason
    except Exception as e:
        return -1, str(e)


def main() -> None:
    p = argparse.ArgumentParser(description="Simulate burst traffic against Nginx proxy")
    p.add_argument(
        "--url",
        default="http://127.0.0.1:80/generate?length=12",
        help="Full URL to hit (default: local proxy /generate)",
    )
    p.add_argument("-n", "--requests", type=int, default=40, help="Total requests")
    p.add_argument("-w", "--workers", type=int, default=20, help="Parallel workers")
    p.add_argument("-t", "--timeout", type=float, default=5.0, help="Per-request timeout")
    args = p.parse_args()

    urls = [args.url] * args.requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda u: one_request(u, args.timeout), urls))

    counts: dict[int, int] = {}
    errors = 0
    for code, err in results:
        if code == -1:
            errors += 1
            print(f"error: {err}", file=sys.stderr)
        else:
            counts[code] = counts.get(code, 0) + 1

    print(f"URL: {args.url}")
    print(f"Total: {args.requests} (workers={args.workers})")
    print("HTTP status counts:", dict(sorted(counts.items())))
    if errors:
        print(f"Transport/other errors: {errors}")


if __name__ == "__main__":
    main()
