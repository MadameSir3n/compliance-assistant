#!/usr/bin/env python3
"""
Compliance Assistant - LLM-powered KYC/AML risk scoring

A FastAPI application for automated compliance screening with explainable AI
and audit logging for regulatory requirements.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
import os
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Compliance Assistant",
    description="LLM-powered KYC/AML risk scoring with explainable AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-fake-key-for-demo"))

# Request models
class ComplianceRequest(BaseModel):
    name: str = Field(..., description="Customer full name")
    address: str = Field(..., description="Customer address")
    transactions: List[Dict] = Field(default_factory=list, description="Transaction history")
    business_type: Optional[str] = Field(default=None, description="Type of business")
    country: Optional[str] = Field(default="US", description="Country code")

class RiskScore(BaseModel):
    score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    confidence: float = Field(..., ge=0, le=100, description="Confidence level")
    label: str = Field(..., description="Risk label (low/medium/high)")

class ComplianceResponse(BaseModel):
    request_id: str
    risk_score: RiskScore
    reasons: List[str]
    recommendations: List[str]
    timestamp: datetime
    model_used: str

# In-memory audit log (use database in production)
audit_log = []

def generate_request_id():
    """Generate a unique request ID."""
    return f"req_{int(datetime.now().timestamp() * 1000)}"

def assess_risk_with_llm(request_data: Dict) -> Dict:
    """
    Assess compliance risk using OpenAI LLM.
    Returns structured risk assessment with explanations.
    """
    try:
        prompt = f"""
        Analyze this customer for KYC/AML compliance risk:
        
        Name: {request_data['name']}
        Address: {request_data['address']}
        Business Type: {request_data.get('business_type', 'Unknown')}
        Country: {request_data.get('country', 'US')}
        Transactions: {len(request_data['transactions'])} transactions
        
        Provide a JSON response with:
        - risk_score: number between 0-100
        - confidence: number between 0-100  
        - risk_label: "low", "medium", or "high"
        - reasons: array of strings explaining the risk factors
        - recommendations: array of strings with compliance recommendations
        
        Return valid JSON only.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a compliance expert specializing in KYC/AML risk assessment. Provide structured, explainable risk analysis with specific reasons and recommendations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        
        # Extract JSON from response
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content
        
        return json.loads(json_str)
        
    except Exception as e:
        logger.error(f"LLM risk assessment failed: {e}")
        # Fallback to basic risk assessment
        return {
            "risk_score": 50.0,
            "confidence": 60.0,
            "risk_label": "medium",
            "reasons": ["Fallback assessment due to technical issues"],
            "recommendations": ["Manual review recommended"]
        }

@app.post("/assess-risk", response_model=ComplianceResponse)
async def assess_risk(request: ComplianceRequest):
    """
    Assess KYC/AML compliance risk for a customer.
    """
    request_id = generate_request_id()
    
    try:
        # Convert request to dict for LLM processing
        request_data = request.dict()
        
        # Get risk assessment from LLM
        assessment = assess_risk_with_llm(request_data)
        
        # Create response
        response = ComplianceResponse(
            request_id=request_id,
            risk_score=RiskScore(
                score=assessment["risk_score"],
                confidence=assessment["confidence"],
                label=assessment["risk_label"]
            ),
            reasons=assessment["reasons"],
            recommendations=assessment["recommendations"],
            timestamp=datetime.now(),
            model_used="gpt-3.5-turbo"
        )
        
        # Log to audit trail
        audit_log.append({
            "request_id": request_id,
            "timestamp": datetime.now(),
            "customer_name": request.name,
            "risk_score": assessment["risk_score"],
            "risk_label": assessment["risk_label"],
            "reasons": assessment["reasons"],
            "model_used": "gpt-3.5-turbo"
        })
        
        logger.info(f"Risk assessment completed: {request_id} - Score: {assessment['risk_score']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@app.get("/audit-log")
async def get_audit_log(limit: int = 10, offset: int = 0):
    """Get audit log entries."""
    return audit_log[offset:offset + limit]

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)