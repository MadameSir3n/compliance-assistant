# Compliance Assistant

An LLM-powered API that assesses KYC/AML compliance risk for financial customers, returning a scored risk label with explainable reasons, recommendations, and a full audit trail.

---

## Problem

KYC/AML compliance reviews are expensive, slow, and inconsistent at scale. Analysts manually read through customer profiles and transaction histories, applying judgment that varies by reviewer and erodes under volume.

## Solution

This assistant accepts a customer profile and transaction list, sends them to GPT with a structured risk-scoring prompt, and returns a scored risk label with confidence rating, human-readable reasons, and recommendations — all logged with a request ID and timestamp for audit purposes.

## Key Features

- AI-powered risk scoring: low / medium / high with confidence rating
- Explainable output: reasons and actionable recommendations on every response
- Audit logging with request IDs and timestamps for regulatory compliance
- Input validation via Pydantic — malformed requests rejected cleanly
- Clean REST API with auto-generated OpenAPI docs at `/docs`
- Runs locally or in Docker in under 60 seconds

## Tech Stack

- **Python** — backend
- **FastAPI** — REST API
- **OpenAI GPT** — risk assessment model
- **Pydantic** — input validation and schema enforcement
- **Docker / Docker Compose** — deployment

## Example Flow

```
1. POST /assess-risk  →  { name, transactions, business_type, country }
2. System builds structured prompt with customer context
3. GPT evaluates: transaction patterns, amounts, geography, declared activity
4. Returns:  risk_score=35.5, label="low", confidence=85.2
5. Reasons: ["Low transaction amounts", "US-based, clear address"]
6. Recommendations: ["Standard monitoring", "Annual KYC update"]
7. Full request logged with request_id and timestamp
```

## How to Run

```bash
git clone https://github.com/MadameSir3n/compliance-assistant.git
cd compliance-assistant
echo "OPENAI_API_KEY=your_key_here" > .env
pip install -r requirements.txt
python main.py
# API:  http://localhost:8000
# Docs: http://localhost:8000/docs
```

Run tests:

```bash
python -m pytest tests/ -v
```

Or with Docker:

```bash
docker-compose up
```

## Known Limitations

- Risk scoring requires an OpenAI API key
- Without a key, the API returns mock scores for demo purposes
- Some components are still being refined
- This is an active development system

## Sample Test Output

```
tests/test_compliance.py::test_health_check PASSED
tests/test_compliance.py::test_risk_assessment PASSED
tests/test_compliance.py::test_high_risk_detection PASSED
tests/test_compliance.py::test_audit_logging PASSED
tests/test_compliance.py::test_invalid_request_rejected PASSED

10 passed in 0.87s
```

## Why This Matters

Manual compliance review doesn't scale. This project demonstrates how LLMs can be applied to structured regulatory tasks — not as a black box, but with explainability and audit trails that make the output trustworthy and defensible in real financial environments.
