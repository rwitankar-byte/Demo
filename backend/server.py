from fastapi import FastAPI, APIRouter, File, UploadFile, Form, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import requests
import base64
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# API Keys
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
HF_TOKEN = os.environ.get('HF_TOKEN')
HF_MODEL_URL = "https://api-inference.huggingface.co/models/Abuzaid01/plant-disease-classifier"

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class ClassificationResponse(BaseModel):
    label: str
    confidence: float

class AdvisoryRequest(BaseModel):
    crop_name: str
    disease_label: str
    confidence: float
    image_base64: str

class AdvisoryResponse(BaseModel):
    visible_symptoms: str
    likely_cause: str
    severity: str
    treatment: str
    preventive_measures: str
    plain_language_advisory: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "CropSense AI API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

@api_router.post("/classify", response_model=ClassificationResponse)
async def classify_disease(file: UploadFile = File(...)):
    """Classify plant disease using HuggingFace model"""
    try:
        # Read the image file
        image_bytes = await file.read()
        
        # Call HuggingFace API
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(HF_MODEL_URL, headers=headers, data=image_bytes)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"HuggingFace API error: {response.text}")
        
        predictions = response.json()
        
        # Get top prediction
        if not predictions or len(predictions) == 0:
            raise HTTPException(status_code=500, detail="No predictions returned")
        
        top_pred = predictions[0]
        
        # Format label: replace ___ with " — ", _ with " ", title case
        formatted_label = top_pred['label'].replace('___', ' — ').replace('_', ' ').title()
        
        return ClassificationResponse(
            label=formatted_label,
            confidence=top_pred['score']
        )
    
    except Exception as e:
        logging.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/advisory", response_model=AdvisoryResponse)
async def get_advisory(request: AdvisoryRequest):
    """Get treatment advisory using Claude AI"""
    try:
        # Initialize Claude chat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"cropsense-{uuid.uuid4()}",
            system_message="You are an expert plant disease specialist. Return ONLY valid JSON — no markdown, no code fences. Schema: {visible_symptoms, likely_cause, severity: Healthy|Mild|Moderate|Severe, treatment, preventive_measures, plain_language_advisory}"
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        # Create user message
        user_text = f"""Analyze this crop disease case:

Crop: {request.crop_name}
Disease Detected: {request.disease_label}
Model Confidence: {request.confidence * 100:.1f}%

Based on the leaf image and disease identification, provide:
1. visible_symptoms: What symptoms are visible on the leaf
2. likely_cause: What causes this disease
3. severity: Classification as Healthy, Mild, Moderate, or Severe
4. treatment: Treatment steps (bullet points)
5. preventive_measures: Prevention steps (bullet points)
6. plain_language_advisory: Simple, actionable advice for farmers in 2-3 sentences

Return ONLY the JSON object, no other text."""

        user_message = UserMessage(text=user_text)
        
        # Get Claude response
        response = await chat.send_message(user_message)
        
        # Parse JSON from response
        try:
            advisory_data = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                advisory_data = json.loads(json_str)
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
                advisory_data = json.loads(json_str)
            else:
                raise ValueError("Invalid JSON response from Claude")
        
        # Convert arrays to strings if needed
        for field in ['treatment', 'preventive_measures']:
            if field in advisory_data and isinstance(advisory_data[field], list):
                advisory_data[field] = '\n'.join(f"• {item}" for item in advisory_data[field])
        
        return AdvisoryResponse(**advisory_data)
    
    except Exception as e:
        logging.error(f"Advisory error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()