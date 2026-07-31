"""Periodic reminder check for upcoming inspection expiry dates.

Full e-mail/notification delivery (docs/03 sections 16.1-16.3) is future
work; this task currently only counts upcoming due schedules so the
scheduler and queue wiring can be verified end-to-end.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.inspections import InspectionSchedule

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.reminders.check_inspection_reminders")
def check_inspection_reminders(within_days: int = 30) -> int:
    db = SessionLocal()
    try:
        cutoff = date.today() + timedelta(days=within_days)
        count = (
            db.query(InspectionSchedule)
            .filter(InspectionSchedule.status == "OPEN", InspectionSchedule.next_due_date <= cutoff)
            .count()
        )
        logger.info("inspection_reminders_due", extra={"count": count, "within_days": within_days})
        return count
    finally:
        db.close()
