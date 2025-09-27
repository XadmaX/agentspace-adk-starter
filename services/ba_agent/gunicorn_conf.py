"""Gunicorn configuration for the BA agent service."""

from __future__ import annotations

import multiprocessing


bind = "0.0.0.0:8000"
workers = max(multiprocessing.cpu_count() // 2, 1)
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 60
graceful_timeout = 30
loglevel = "info"
