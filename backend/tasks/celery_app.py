"""
Project: AlphaQuant AI
File: backend/tasks/celery_app.py
Description: Celery application factory and configuration.
Python Version: 3.11.9
"""

from __future__ import annotations

from celery import Celery

from backend.core.config import settings


def create_celery_app() -> Celery:
    """
    Create configured Celery application.

    Returns:
        Configured Celery instance.
    """
    celery_app = Celery(settings.celery_app_name)
    celery_app.conf.update(settings.celery_config)
    celery_app.autodiscover_tasks(["backend.tasks"])
    return celery_app


celery_app = create_celery_app()

