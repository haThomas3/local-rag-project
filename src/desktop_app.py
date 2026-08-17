from __future__ import annotations

import threading
import time
import urllib.error
import urllib.request

import uvicorn
import webview

from src.api import app


HOST = "127.0.0.1"
PORT = 8000


def _run_server() -> None:
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


def _wait_for_server(url: str, timeout_seconds: float = 15.0) -> None:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except urllib.error.URLError:
            time.sleep(0.2)

    raise RuntimeError(f"Server did not become ready at {url} within {timeout_seconds}s")


def main() -> None:
    server_thread = threading.Thread(target=_run_server, daemon=True)
    server_thread.start()

    _wait_for_server(f"http://{HOST}:{PORT}/health")

    webview.create_window("Local RAG", f"http://{HOST}:{PORT}", width=960, height=720)
    webview.start()


if __name__ == "__main__":
    main()
