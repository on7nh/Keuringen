"""Inspection expiry calculation per docs/01_Functioneel_Ontwerp.md.

expiry_date = inspection_date + discipline validity term.
Falls back to report_date, then to manual entry, when no inspection date is
available. If the discipline has no configured validity term, no expiry
date is computed automatically.
"""

from __future__ import annotations

from datetime import date

from dateutil.relativedelta import relativedelta

from app.models.organization import Discipline


def calculate_expiry_date(
    discipline: Discipline, *, inspection_date: date | None, report_date: date | None
) -> date | None:
    reference_date = inspection_date or report_date
    if reference_date is None:
        return None
    if discipline.validity_value is None or discipline.validity_unit is None:
        return None

    if discipline.validity_unit == "day":
        return reference_date + relativedelta(days=discipline.validity_value)
    if discipline.validity_unit == "month":
        return reference_date + relativedelta(months=discipline.validity_value)
    if discipline.validity_unit == "year":
        return reference_date + relativedelta(years=discipline.validity_value)

    raise ValueError(f"Unknown validity_unit '{discipline.validity_unit}'")
