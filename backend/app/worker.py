"""Entry point for the Celery worker process (docker-compose `worker` service)."""

from app.celery_app import celery_app

if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=INFO"])
