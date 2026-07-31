"""Entry point for the Celery beat scheduler process (docker-compose `scheduler` service)."""

from app.celery_app import celery_app

if __name__ == "__main__":
    celery_app.Beat(loglevel="INFO").run()
