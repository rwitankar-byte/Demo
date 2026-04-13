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
from groq import Groq
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
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
HF_MODEL_URL = "https://api-inference.huggingface.co/models/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

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


def classify_with_huggingface(image_bytes):
    """Try HuggingFace API first"""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(HF_MODEL_URL, headers=headers, data=image_bytes, timeout=30)
    if response.status_code != 200:
        raise Exception(f"HuggingFace API error: {response.status_code}")
    predictions = response.json()
    if isinstance(predictions, list) and len(predictions) > 0:
        top_pred = predictions[0]
        formatted_label = top_pred['label'].replace('___', ' — ').replace('_', ' ').title()
        return formatted_label, top_pred['score']
    raise Exception("No predictions returned from HuggingFace")


def classify_with_groq(image_base64, crop_name="Unknown"):
    """Fallback: Use Groq vision model to classify disease"""
    completion = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are an expert plant pathologist. Analyze this leaf image and identify the plant disease.
                        
The farmer selected crop type: {crop_name}

Return ONLY a valid JSON object with exactly these fields:
- "label": The disease name in format "CropName — DiseaseName" (e.g., "Tomato — Early Blight"). If healthy, use "CropName — Healthy"
- "confidence": A float between 0.0 and 1.0 representing your confidence

Return ONLY the JSON, no other text."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        temperature=0.1,
        max_tokens=256,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(completion.choices[0].message.content)
    return result.get("label", "Unknown Disease"), result.get("confidence", 0.85)


def get_advisory_from_groq(crop_name, disease_label, confidence):
    """Fallback: Use Groq for advisory when Claude fails"""
    completion = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": "You are an expert plant disease specialist. Return ONLY valid JSON — no markdown, no code fences."
            },
            {
                "role": "user",
                "content": f"""Analyze this crop disease case:

Crop: {crop_name}
Disease Detected: {disease_label}
Model Confidence: {confidence * 100:.1f}%

Return ONLY a JSON object with these exact fields:
- "visible_symptoms": What symptoms are typically visible (string)
- "likely_cause": What causes this disease (string)
- "severity": One of "Healthy", "Mild", "Moderate", or "Severe" (string)
- "treatment": Treatment steps as a single string with bullet points
- "preventive_measures": Prevention steps as a single string with bullet points
- "plain_language_advisory": Simple farmer advice in 2-3 sentences (string)"""
            }
        ],
        temperature=0.3,
        max_tokens=800,
        response_format={"type": "json_object"}
    )
    
    return json.loads(completion.choices[0].message.content)


@api_router.post("/classify", response_model=ClassificationResponse)
async def classify_disease(file: UploadFile = File(...), crop_name: str = Form(default="Unknown")):
    """Classify plant disease — tries HuggingFace first, falls back to Groq vision"""
    try:
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Try HuggingFace first
        try:
            label, confidence = classify_with_huggingface(image_bytes)
            logger.info(f"HuggingFace classification: {label} ({confidence:.2%})")
            return ClassificationResponse(label=label, confidence=confidence)
        except Exception as hf_error:
            logger.warning(f"HuggingFace failed, falling back to Groq: {hf_error}")
        
        # Fallback to Groq vision
        label, confidence = classify_with_groq(image_base64, crop_name)
        logger.info(f"Groq classification: {label} ({confidence:.2%})")
        return ClassificationResponse(label=label, confidence=confidence)
    
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/advisory", response_model=AdvisoryResponse)
async def get_advisory(request: AdvisoryRequest):
    """Get treatment advisory — tries Claude first, falls back to Groq"""
    advisory_data = None
    
    # Try Claude (Emergent LLM) first
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"cropsense-{uuid.uuid4()}",
            system_message="You are an expert plant disease specialist. Return ONLY valid JSON — no markdown, no code fences. Schema: {visible_symptoms, likely_cause, severity: Healthy|Mild|Moderate|Severe, treatment, preventive_measures, plain_language_advisory}"
        ).with_model("anthropic", "claude-sonnet-4-20250514")
        
        user_text = f"""Analyze this crop disease case:

Crop: {request.crop_name}
Disease Detected: {request.disease_label}
Model Confidence: {request.confidence * 100:.1f}%

Based on the disease identification, provide:
1. visible_symptoms: What symptoms are visible on the leaf
2. likely_cause: What causes this disease
3. severity: Classification as Healthy, Mild, Moderate, or Severe
4. treatment: Treatment steps (bullet points)
5. preventive_measures: Prevention steps (bullet points)
6. plain_language_advisory: Simple, actionable advice for farmers in 2-3 sentences

Return ONLY the JSON object, no other text."""

        user_message = UserMessage(text=user_text)
        response = await chat.send_message(user_message)
        
        try:
            advisory_data = json.loads(response)
        except json.JSONDecodeError:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                advisory_data = json.loads(json_str)
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
                advisory_data = json.loads(json_str)
            else:
                raise ValueError("Invalid JSON from Claude")
        
        logger.info("Claude advisory generated successfully")
    
    except Exception as claude_error:
        logger.warning(f"Claude failed, falling back to Groq: {claude_error}")
        
        # Fallback to Groq
        try:
            advisory_data = get_advisory_from_groq(
                request.crop_name, request.disease_label, request.confidence
            )
            logger.info("Groq advisory generated successfully (fallback)")
        except Exception as groq_error:
            logger.error(f"Groq advisory also failed: {groq_error}")
            raise HTTPException(status_code=500, detail=f"Both Claude and Groq advisory failed: {str(groq_error)}")
    
    # Convert arrays to strings if needed
    for field in ['treatment', 'preventive_measures']:
        if field in advisory_data and isinstance(advisory_data[field], list):
            advisory_data[field] = '\n'.join(f"• {item}" for item in advisory_data[field])
    
    return AdvisoryResponse(**advisory_data)


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
