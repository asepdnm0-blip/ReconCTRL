"""
Celery entrypoint for Docker worker image (re-exports backend app.worker).
"""

import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.worker.celery_app import celery_app  # noqa: F401
from app.worker import tasks as _tasks  # noqa: F401

__all__ = ["celery_app"]
