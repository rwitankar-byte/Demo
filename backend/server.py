import base64
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

try:
    from groq import Groq
except ImportError:  # pragma: no cover
    Groq = None


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

HF_TOKEN = os.environ.get("HF_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HF_MODEL_URL = (
    "https://api-inference.huggingface.co/models/"
    "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
)

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY and Groq else None

app = FastAPI(title="CropSense AI API")
api_router = APIRouter(prefix="/api")


LANGUAGE_INSTRUCTIONS = {
    "en": "Respond entirely in English.",
    "hi": "Respond entirely in Hindi (हिन्दी). Use Devanagari script. All field values must be in Hindi.",
    "mr": "Respond entirely in Marathi (मराठी). Use Devanagari script. All field values must be in Marathi.",
}


class ClassificationResponse(BaseModel):
    label: str
    confidence: float
    provider: Optional[str] = None


class AdvisoryRequest(BaseModel):
    crop_name: str
    disease_label: str
    confidence: float
    image_base64: str
    language: str = "en"


class AdvisoryResponse(BaseModel):
    visible_symptoms: str
    likely_cause: str
    severity: str
    treatment: str
    preventive_measures: str
    plain_language_advisory: str
    provider: Optional[str] = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def severity_from_label(label: str, confidence: float) -> str:
    if "healthy" in label.lower():
        return "Healthy"
    if confidence < 0.45:
        return "Mild"
    if confidence < 0.75:
        return "Moderate"
    return "Severe"


def fallback_classification(crop_name: str) -> Dict[str, Any]:
    crop = crop_name.strip() if crop_name and crop_name.strip() else "Unknown Crop"
    return {
        "label": f"{crop} — Needs Expert Review",
        "confidence": 0.35,
        "provider": "fallback",
    }


def fallback_advisory(
    crop_name: str, disease_label: str, confidence: float, language: str
) -> Dict[str, Any]:
    severity = severity_from_label(disease_label, confidence)
    crop = crop_name or "the crop"

    english = {
        "visible_symptoms": (
            f"{crop} may show spotting, yellowing, wilting, curling, or damaged tissue "
            "based on the uploaded image."
        ),
        "likely_cause": (
            "The image could not be fully confirmed by the live advisory provider, so this "
            "is a safe fallback explanation. The issue may involve disease, pests, or stress."
        ),
        "severity": severity,
        "treatment": (
            "• Remove heavily affected leaves if possible.\n"
            "• Avoid overwatering and improve airflow.\n"
            "• Confirm treatment with a local agriculture expert before spraying chemicals."
        ),
        "preventive_measures": (
            "• Inspect leaves regularly.\n"
            "• Use clean tools and healthy planting material.\n"
            "• Avoid wetting leaves during irrigation."
        ),
        "plain_language_advisory": (
            f"The system detected '{disease_label}' with limited live support. "
            "Please treat this as an early warning and confirm locally if symptoms spread."
        ),
        "provider": "fallback",
    }

    hindi = {
        "visible_symptoms": "पत्तियों पर धब्बे, पीला पड़ना, मुरझाना, मुड़ना या नुकसान दिख सकता है।",
        "likely_cause": "लाइव सलाह सेवा उपलब्ध न होने पर यह सुरक्षित फॉलबैक उत्तर है। समस्या रोग, कीट या पौधे के तनाव से जुड़ी हो सकती है।",
        "severity": severity,
        "treatment": "• बहुत प्रभावित पत्तियों को हटाएं।\n• अधिक पानी देने से बचें और हवा का प्रवाह बढ़ाएं।\n• रसायन छिड़कने से पहले कृषि विशेषज्ञ से सलाह लें।",
        "preventive_measures": "• पत्तियों की नियमित जांच करें।\n• साफ औजार और स्वस्थ पौध सामग्री का उपयोग करें।\n• सिंचाई के समय पत्तियों को गीला करने से बचें।",
        "plain_language_advisory": f"सिस्टम ने '{disease_label}' का संकेत दिया है। इसे शुरुआती चेतावनी मानें और लक्षण बढ़ने पर स्थानीय विशेषज्ञ से पुष्टि करें।",
        "provider": "fallback",
    }

    marathi = {
        "visible_symptoms": "पानांवर डाग, पिवळेपणा, कोमेजणे, वाकणे किंवा नुकसान दिसू शकते.",
        "likely_cause": "लाइव्ह सल्ला सेवा उपलब्ध नसल्यास हा सुरक्षित फॉलबॅक प्रतिसाद आहे. समस्या रोग, किडी किंवा ताणाशी संबंधित असू शकते.",
        "severity": severity,
        "treatment": "• जास्त बाधित पाने काढा.\n• जास्त पाणी देणे टाळा आणि हवा खेळती ठेवा.\n• रासायनिक फवारणीपूर्वी कृषी तज्ञांचा सल्ला घ्या.",
        "preventive_measures": "• पानांची नियमित तपासणी करा.\n• स्वच्छ साधने आणि निरोगी लागवड साहित्य वापरा.\n• पानांवर पाणी पडणार नाही याची काळजी घ्या.",
        "plain_language_advisory": f"सिस्टमने '{disease_label}' असा इशारा दिला आहे. हे प्राथमिक चेतावणी समजा आणि लक्षणे वाढल्यास स्थानिक तज्ञांकडून खात्री करा.",
        "provider": "fallback",
    }

    return {"en": english, "hi": hindi, "mr": marathi}.get(language, english)


def classify_with_huggingface(image_bytes: bytes) -> Dict[str, Any]:
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is not configured")

    response = requests.post(
        HF_MODEL_URL,
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        data=image_bytes,
        timeout=30,
    )
    response.raise_for_status()
    predictions = response.json()

    if isinstance(predictions, list) and predictions:
        top_pred = predictions[0]
        return {
            "label": top_pred["label"].replace("___", " — ").replace("_", " ").title(),
            "confidence": float(top_pred["score"]),
            "provider": "huggingface",
        }

    raise RuntimeError("No predictions returned from Hugging Face")


def classify_with_groq(image_base64: str, crop_name: str = "Unknown") -> Dict[str, Any]:
    if not groq_client:
        raise RuntimeError("Groq is not configured")

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
- "label": The disease name in format "CropName — DiseaseName". If healthy, use "CropName — Healthy"
- "confidence": A float between 0.0 and 1.0

Return ONLY the JSON, no other text.""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
        temperature=0.1,
        max_tokens=256,
        response_format={"type": "json_object"},
    )
    result = json.loads(completion.choices[0].message.content)
    return {
        "label": result.get("label", "Unknown Disease"),
        "confidence": float(result.get("confidence", 0.85)),
        "provider": "groq",
    }


def get_advisory_from_groq(
    crop_name: str, disease_label: str, confidence: float, language: str = "en"
) -> Dict[str, Any]:
    if not groq_client:
        raise RuntimeError("Groq is not configured")

    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["en"])
    completion = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert plant disease specialist. Return ONLY valid JSON "
                    f"with no markdown or code fences. {lang_instruction}"
                ),
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
- "severity": One of "Healthy", "Mild", "Moderate", or "Severe" (always in English)
- "treatment": Treatment steps as a single string with bullet points
- "preventive_measures": Prevention steps as a single string with bullet points
- "plain_language_advisory": Simple farmer advice in 2-3 sentences

{lang_instruction}""",
            },
        ],
        temperature=0.3,
        max_tokens=1200,
        response_format={"type": "json_object"},
    )
    advisory_data = json.loads(completion.choices[0].message.content)
    advisory_data["provider"] = "groq"
    return advisory_data


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("CropSense AI stateless backend started")


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "CropSense AI Backend",
        "timestamp": now_iso(),
        "storage": "disabled",
        "providers": {
            "huggingface": "configured" if HF_TOKEN else "missing",
            "groq": "configured" if groq_client else "fallback-only",
        },
    }


@api_router.get("/")
async def root() -> Dict[str, str]:
    return {"message": "CropSense AI API"}


@api_router.get("/health")
async def api_health_check() -> Dict[str, Any]:
    return await health_check()


@api_router.post("/classify", response_model=ClassificationResponse)
async def classify_disease(
    file: UploadFile = File(...), crop_name: str = Form(default="Unknown")
) -> ClassificationResponse:
    try:
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        providers = (
            lambda: classify_with_huggingface(image_bytes),
            lambda: classify_with_groq(image_base64, crop_name),
            lambda: fallback_classification(crop_name),
        )

        for provider in providers:
            try:
                result = provider()
                logger.info(
                    "Classification completed using %s", result.get("provider", "unknown")
                )
                return ClassificationResponse(**result)
            except Exception as exc:
                logger.warning("Classification provider failed: %s", exc)

        raise RuntimeError("No classification provider returned a result")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@api_router.post("/advisory", response_model=AdvisoryResponse)
async def get_advisory(request: AdvisoryRequest) -> AdvisoryResponse:
    try:
        advisory_data = get_advisory_from_groq(
            request.crop_name,
            request.disease_label,
            request.confidence,
            request.language or "en",
        )
        for field in ["treatment", "preventive_measures"]:
            if field in advisory_data and isinstance(advisory_data[field], list):
                advisory_data[field] = "\n".join(
                    f"• {item}" for item in advisory_data[field]
                )
        return AdvisoryResponse(**advisory_data)
    except Exception as exc:
        logger.warning("Groq advisory failed, using fallback: %s", exc)
        return AdvisoryResponse(
            **fallback_advisory(
                request.crop_name,
                request.disease_label,
                request.confidence,
                request.language or "en",
            )
        )


app.include_router(api_router)

cors_origins = [origin.strip() for origin in os.environ.get("CORS_ORIGINS", "*").split(",")]
allow_all_origins = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_credentials=not allow_all_origins,
    allow_origins=["*"] if allow_all_origins else cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
