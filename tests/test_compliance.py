"""
Unit/integration tests for the Compliance Assistant backend.
OpenAI calls are mocked so no API key is required.
Uses httpx.AsyncClient + ASGITransport (compatible with httpx >= 0.20).
"""
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import httpx

# Ensure backend/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from main import app, audit_log


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _async_call(method: str, url: str, **kwargs):
    """Make an async HTTP call directly into the ASGI app."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        return await getattr(c, method)(url, **kwargs)


def _call(method: str, url: str, **kwargs):
    """Synchronous wrapper around _async_call."""
    return asyncio.run(_async_call(method, url, **kwargs))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_audit_log():
    audit_log.clear()
    yield
    audit_log.clear()


def _mock_llm_response(risk_score=25.0, confidence=90.0, risk_label="low"):
    payload = json.dumps({
        "risk_score": risk_score,
        "confidence": confidence,
        "risk_label": risk_label,
        "reasons": ["Short transaction history"],
        "recommendations": ["Standard monitoring applies"],
    })
    mock_choice = MagicMock()
    mock_choice.message.content = payload
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


VALID_PAYLOAD = {
    "name": "Jane Doe",
    "address": "123 Main St, Springfield, US",
    "transactions": [{"amount": 500, "currency": "USD", "date": "2024-01-15"}],
    "business_type": "retail",
    "country": "US",
}


# ── Health check ──────────────────────────────────────────────────────────────

def test_health_endpoint_returns_200():
    r = _call("get", "/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


# ── /assess-risk ──────────────────────────────────────────────────────────────

class TestAssessRisk:
    def test_low_risk_happy_path(self):
        with patch("main.client.chat.completions.create",
                   return_value=_mock_llm_response(25.0, 90.0, "low")):
            r = _call("post", "/assess-risk", json=VALID_PAYLOAD)
        assert r.status_code == 200
        data = r.json()
        assert data["risk_score"]["score"] == 25.0
        assert data["risk_score"]["label"] == "low"

    def test_response_has_required_fields(self):
        with patch("main.client.chat.completions.create",
                   return_value=_mock_llm_response()):
            r = _call("post", "/assess-risk", json=VALID_PAYLOAD)
        data = r.json()
        for field in ("request_id", "risk_score", "reasons", "recommendations",
                      "timestamp", "model_used"):
            assert field in data, f"Missing field: {field}"

    def test_request_id_prefixed_with_req(self):
        with patch("main.client.chat.completions.create",
                   return_value=_mock_llm_response()):
            r = _call("post", "/assess-risk", json=VALID_PAYLOAD)
        assert r.json()["request_id"].startswith("req_")

    def test_llm_failure_returns_fallback_medium_risk(self):
        with patch("main.client.chat.completions.create", side_effect=Exception("timeout")):
            r = _call("post", "/assess-risk", json=VALID_PAYLOAD)
        assert r.status_code == 200
        assert r.json()["risk_score"]["label"] == "medium"

    def test_missing_required_field_returns_422(self):
        bad_payload = {"address": "No name field here"}
        r = _call("post", "/assess-risk", json=bad_payload)
        assert r.status_code == 422

    def test_assess_risk_writes_to_audit_log(self):
        with patch("main.client.chat.completions.create",
                   return_value=_mock_llm_response()):
            _call("post", "/assess-risk", json=VALID_PAYLOAD)
        assert len(audit_log) == 1
        assert audit_log[0]["customer_name"] == "Jane Doe"


# ── /audit-log ────────────────────────────────────────────────────────────────

class TestAuditLog:
    def test_empty_log_returns_empty_list(self):
        r = _call("get", "/audit-log")
        assert r.status_code == 200
        assert r.json() == []

    def test_log_entry_appears_after_assessment(self):
        with patch("main.client.chat.completions.create",
                   return_value=_mock_llm_response(75.0, 85.0, "high")):
            _call("post", "/assess-risk", json=VALID_PAYLOAD)
        entries = _call("get", "/audit-log").json()
        assert len(entries) == 1
        assert entries[0]["risk_label"] == "high"

    def test_limit_parameter_respected(self):
        with patch("main.client.chat.completions.create",
                   return_value=_mock_llm_response()):
            for _ in range(5):
                _call("post", "/assess-risk", json=VALID_PAYLOAD)
        r = _call("get", "/audit-log?limit=2")
        assert len(r.json()) == 2

