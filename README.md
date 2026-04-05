# Compliance Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5%2B-purple.svg)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Compliance](https://img.shields.io/badge/Compliance-KYC%2FAML-lightgrey.svg)](https://github.com/MadameSir3n/compliance-assistant)
[![Audit](https://img.shields.io/badge/Audit-Logging-blue.svg)](https://github.com/MadameSir3n/compliance-assistant)

LLM-powered KYC/AML risk scoring and compliance assistant for financial applications.

## 🚀 Features

- **AI-Powered Risk Assessment**: Uses OpenAI GPT for intelligent risk scoring
- **Explainable Results**: Provides detailed reasons and recommendations
- **Audit Logging**: Comprehensive audit trail for regulatory compliance
- **RESTful API**: FastAPI backend with OpenAPI documentation
- **Dockerized**: Easy deployment with Docker Compose

## 📋 Quick Start

```bash
# Clone the repository
git clone https://github.com/MadameSir3n/compliance-assistant.git
cd compliance-assistant

# Set up environment variables
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Start the application
docker-compose up

# API will be available at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🎯 API Usage

### Assess Compliance Risk

```bash
curl -X POST "http://localhost:8000/assess-risk" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "address": "123 Main St, New York, NY 10001",
    "transactions": [
      {"amount": 1500, "currency": "USD", "description": "Equipment purchase"},
      {"amount": 500, "currency": "USD", "description": "Software subscription"}
    ],
    "business_type": "Technology Consulting",
    "country": "US"
  }'
```

### Response Format

```json
{
  "request_id": "req_1704067200000",
  "risk_score": {
    "score": 35.5,
    "confidence": 85.2,
    "label": "low"
  },  
  "reasons": [
    "Low transaction amounts consistent with business type",
    "US-based business with clear address"
  ],
  "recommendations": [
    "Standard monitoring recommended",
    "Update KYC documentation annually"
  ],
  "timestamp": "2023-12-31T23:59:59.999999",
  "model_used": "gpt-3.5-turbo"
}
```

## 🏗️ Architecture

```
compliance-assistant/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Container configuration
├── docker-compose.yml      # Multi-container setup
└── README.md              # This file
```

## 🔧 Development

### Local Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Testing

```bash
# Run tests
pytest tests/

# Test API endpoints
curl http://localhost:8000/health
```

## 📊 Risk Assessment Scale

- **0-30**: Low risk - Standard monitoring
- **31-70**: Medium risk - Enhanced due diligence  
- **71-100**: High risk - Manual review required

## 🔒 Security Features

- Input validation with Pydantic
- Audit logging for compliance
- Environment variable configuration
- No sensitive data storage

## 🚧 Future Enhancements

- [ ] Frontend React application
- [ ] Database persistence
- [ ] Advanced risk models
- [ ] Regulatory rule engine
- [ ] Batch processing
- [ ] Export capabilities

## 📝 License

MIT License - see LICENSE file for details.
