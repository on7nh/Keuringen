"""Field extraction for keuringsdocumenten (docs/01 "Herkende gegevens").

Two engines are supported, selected automatically:

- Rule-based (default, always available): regex/keyword matching for
  examination/report dates and keuringsstatus. Fully local, no network,
  deterministic - this is what's actually tested in this environment.
- LLM gateway (optional): if AI_GATEWAY_URL is configured, delegates to an
  OpenAI-compatible chat completions endpoint (e.g. a local vLLM/Ollama
  server) with a structured-output prompt, per docs/04 section 5.3. This
  path is implemented but could not be exercised against a real model
  server in this environment - see PROGRESS.md.

Site and discipline are deliberately not extracted here: both are required
inputs at upload time (see app/services/document_service.py) rather than
AI-inferred, so re-extracting them would be redundant.
"""

from __future__ import annotations

import json
import re
from datetime import date

import httpx

from app.core.config import get_settings

settings = get_settings()

EXAMINATION_DATE = "EXAMINATION_DATE"
REPORT_DATE = "REPORT_DATE"
INSPECTION_STATUS = "INSPECTION_STATUS"

DUTCH_MONTHS = {
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}

_DATE_NUMERIC_RE = re.compile(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})")
_DATE_TEXTUAL_RE = re.compile(
    r"(\d{1,2})\s+(" + "|".join(DUTCH_MONTHS) + r")\s+(\d{4})", re.IGNORECASE
)

EXAMINATION_DATE_LABELS = ["datum van onderzoek", "onderzoeksdatum", "datum onderzoek", "datum keuring"]
REPORT_DATE_LABELS = ["datum van verslag", "verslagdatum", "datum verslag", "datum rapport"]

# Ordered so the more specific phrase is matched before its substring.
STATUS_KEYWORDS: list[tuple[str, list[str]]] = [
    ("APPROVED_WITH_REMARKS", ["goedgekeurd met opmerkingen", "goedgekeurd, met opmerkingen"]),
    ("APPROVED", ["goedgekeurd"]),
    ("REJECTED", ["afgekeurd", "niet goedgekeurd"]),
]


def _parse_date(day: str, month: int | str, year: str) -> date | None:
    try:
        return date(int(year), int(month), int(day))
    except (ValueError, TypeError):
        return None


def _find_dates_near_labels(text: str, labels: list[str]) -> list[tuple[date, str]]:
    lowered = text.lower()
    found: list[tuple[date, str]] = []
    for label in labels:
        for m in re.finditer(re.escape(label), lowered):
            window = text[m.end() : m.end() + 60]
            numeric = _DATE_NUMERIC_RE.search(window)
            if numeric:
                parsed = _parse_date(numeric.group(1), numeric.group(2), numeric.group(3))
                if parsed:
                    found.append((parsed, " ".join(window[:40].split())))
                    continue
            textual = _DATE_TEXTUAL_RE.search(window)
            if textual:
                parsed = _parse_date(textual.group(1), DUTCH_MONTHS.get(textual.group(2).lower(), 0), textual.group(3))
                if parsed:
                    found.append((parsed, " ".join(window[:40].split())))
    return found


def extract_fields_rule_based(text: str) -> dict[str, dict]:
    predictions: dict[str, dict] = {}

    exam_dates = _find_dates_near_labels(text, EXAMINATION_DATE_LABELS)
    if exam_dates:
        value, snippet = exam_dates[0]
        predictions[EXAMINATION_DATE] = {"value": value.isoformat(), "confidence": 0.7, "snippet": snippet}

    report_dates = _find_dates_near_labels(text, REPORT_DATE_LABELS)
    if report_dates:
        value, snippet = report_dates[0]
        predictions[REPORT_DATE] = {"value": value.isoformat(), "confidence": 0.7, "snippet": snippet}

    lowered = text.lower()
    for code, keywords in STATUS_KEYWORDS:
        for keyword in keywords:
            idx = lowered.find(keyword)
            if idx != -1:
                snippet_start = max(0, idx - 15)
                snippet_end = idx + len(keyword) + 15
                snippet = " ".join(text[snippet_start:snippet_end].split())
                predictions[INSPECTION_STATUS] = {"value": code, "confidence": 0.6, "snippet": snippet}
                break
        if INSPECTION_STATUS in predictions:
            break

    return predictions


_LLM_SYSTEM_PROMPT = """Je analyseert een Nederlandstalig keuringsdocument.
Retourneer uitsluitend geldige JSON, zonder toelichting, met exact deze velden:
{"examination_date": "YYYY-MM-DD of null", "report_date": "YYYY-MM-DD of null", "inspection_status": "APPROVED, APPROVED_WITH_REMARKS, REJECTED of null"}
Verzin geen gegevens die niet letterlijk in de tekst staan. Gebruik null wanneer iets niet duidelijk vermeld is."""


def is_llm_configured() -> bool:
    return bool(settings.ai_gateway_url)


def extract_fields_via_llm(text: str) -> dict[str, dict] | None:
    """Optional path per docs/04 §5.3 - an OpenAI-compatible chat completions
    call to a local model server. Returns None on any failure so the caller
    falls back to the rule-based engine; never raises to the job runner.
    """
    if not settings.ai_gateway_url:
        return None
    try:
        response = httpx.post(
            f"{settings.ai_gateway_url.rstrip('/')}/v1/chat/completions",
            json={
                "model": settings.ai_gateway_model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": _LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": text[:6000]},
                ],
            },
            timeout=settings.ai_gateway_timeout_seconds,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except Exception:
        return None

    predictions: dict[str, dict] = {}
    if parsed.get("examination_date"):
        predictions[EXAMINATION_DATE] = {"value": parsed["examination_date"], "confidence": None, "snippet": None}
    if parsed.get("report_date"):
        predictions[REPORT_DATE] = {"value": parsed["report_date"], "confidence": None, "snippet": None}
    if parsed.get("inspection_status") in ("APPROVED", "APPROVED_WITH_REMARKS", "REJECTED"):
        predictions[INSPECTION_STATUS] = {"value": parsed["inspection_status"], "confidence": None, "snippet": None}
    return predictions


def extract_fields(text: str) -> tuple[dict[str, dict], str]:
    """Returns (predictions, model_identifier) - tries the LLM gateway first
    when configured, falling back to the rule-based engine on any failure
    or when no gateway is configured."""
    if is_llm_configured():
        llm_predictions = extract_fields_via_llm(text)
        if llm_predictions:
            return llm_predictions, f"llm-gateway:{settings.ai_gateway_model}"
    return extract_fields_rule_based(text), "rule-based-v1"
