import base64
import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.cors import CORSMiddleware

try:
    from groq import Groq
except ImportError:  # pragma: no cover - optional dependency at runtime
    Groq = None

try:
    from supabase import create_client
except ImportError:  # pragma: no cover - optional dependency at runtime
    create_client = None


ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
SQLITE_PATH = DATA_DIR / "local.db"
load_dotenv(ROOT_DIR / ".env")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HF_MODEL_URL = (
    "https://api-inference.huggingface.co/models/"
    "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now_utc().isoformat()


class BaseStorage:
    mode = "unknown"

    def health(self) -> Dict[str, str]:
        return {"mode": self.mode, "status": "unknown"}

    def insert_status_check(self, payload: Dict[str, Any]) -> None:
        raise NotImplementedError

    def list_status_checks(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def insert_diagnosis(self, payload: Dict[str, Any]) -> None:
        raise NotImplementedError

    def list_diagnoses(self, limit: int = 50) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def delete_diagnosis(self, record_id: str) -> bool:
        raise NotImplementedError

    def clear_diagnoses(self) -> None:
        raise NotImplementedError


class SQLiteStorage(BaseStorage):
    mode = "sqlite"

    def __init__(self, db_path: Path) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS status_checks (
                    id TEXT PRIMARY KEY,
                    client_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS diagnoses (
                    id TEXT PRIMARY KEY,
                    crop_name TEXT NOT NULL,
                    disease_label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    severity TEXT NOT NULL,
                    visible_symptoms TEXT NOT NULL,
                    likely_cause TEXT NOT NULL,
                    treatment TEXT NOT NULL,
                    preventive_measures TEXT NOT NULL,
                    plain_language_advisory TEXT NOT NULL,
                    language TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def health(self) -> Dict[str, str]:
        return {"mode": self.mode, "status": "connected"}

    def insert_status_check(self, payload: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO status_checks (id, client_name, timestamp) VALUES (?, ?, ?)",
                (payload["id"], payload["client_name"], payload["timestamp"]),
            )
            conn.commit()

    def list_status_checks(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, client_name, timestamp FROM status_checks ORDER BY timestamp DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def insert_diagnosis(self, payload: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO diagnoses (
                    id, crop_name, disease_label, confidence, severity,
                    visible_symptoms, likely_cause, treatment,
                    preventive_measures, plain_language_advisory,
                    language, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["id"],
                    payload["crop_name"],
                    payload["disease_label"],
                    payload["confidence"],
                    payload["severity"],
                    payload["visible_symptoms"],
                    payload["likely_cause"],
                    payload["treatment"],
                    payload["preventive_measures"],
                    payload["plain_language_advisory"],
                    payload["language"],
                    payload["timestamp"],
                ),
            )
            conn.commit()

    def list_diagnoses(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, crop_name, disease_label, confidence, severity,
                       visible_symptoms, likely_cause, treatment,
                       preventive_measures, plain_language_advisory,
                       language, timestamp
                FROM diagnoses
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_diagnosis(self, record_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM diagnoses WHERE id = ?", (record_id,))
            conn.commit()
        return cursor.rowcount > 0

    def clear_diagnoses(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM diagnoses")
            conn.commit()


class SupabaseStorage(BaseStorage):
    mode = "supabase"

    def __init__(self, url: str, service_role_key: str) -> None:
        if not create_client:
            raise RuntimeError("supabase package is not installed")
        self.client = create_client(url, service_role_key)

    @staticmethod
    def _result_data(result: Any) -> Any:
        return getattr(result, "data", result)

    def health(self) -> Dict[str, str]:
        try:
            self.client.table("status_checks").select("id").limit(1).execute()
            return {"mode": self.mode, "status": "connected"}
        except Exception as exc:  # pragma: no cover - depends on external service
            logger.warning("Supabase health check failed: %s", exc)
            return {"mode": self.mode, "status": "degraded"}

    def insert_status_check(self, payload: Dict[str, Any]) -> None:
        self.client.table("status_checks").insert(payload).execute()

    def list_status_checks(self) -> List[Dict[str, Any]]:
        result = self.client.table("status_checks").select("*").order(
            "timestamp", desc=True
        ).execute()
        return self._result_data(result) or []

    def insert_diagnosis(self, payload: Dict[str, Any]) -> None:
        self.client.table("diagnoses").insert(payload).execute()

    def list_diagnoses(self, limit: int = 50) -> List[Dict[str, Any]]:
        result = (
            self.client.table("diagnoses")
            .select("*")
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return self._result_data(result) or []

    def delete_diagnosis(self, record_id: str) -> bool:
        result = self.client.table("diagnoses").delete().eq("id", record_id).execute()
        return bool(self._result_data(result))

    def clear_diagnoses(self) -> None:
        self.client.table("diagnoses").delete().neq("id", "").execute()


def build_storage() -> BaseStorage:
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        logger.info("Using Supabase storage backend")
        return SupabaseStorage(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    logger.info("Using local SQLite storage backend at %s", SQLITE_PATH)
    return SQLiteStorage(SQLITE_PATH)


storage = build_storage()
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY and Groq else None


app = FastAPI(title="CropSense AI API")
api_router = APIRouter(prefix="/api")


LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "mr": "Marathi (मराठी)",
}

LANGUAGE_INSTRUCTIONS = {
    "en": "Respond entirely in English.",
    "hi": "Respond entirely in Hindi (हिन्दी). Use Devanagari script. All field values must be in Hindi.",
    "mr": "Respond entirely in Marathi (मराठी). Use Devanagari script. All field values must be in Marathi.",
}


class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=now_utc)


class StatusCheckCreate(BaseModel):
    client_name: str


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


class DiagnosisRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    crop_name: str
    disease_label: str
    confidence: float
    severity: str
    visible_symptoms: str
    likely_cause: str
    treatment: str
    preventive_measures: str
    plain_language_advisory: str
    language: str = "en"
    timestamp: str = Field(default_factory=now_iso)


class DiagnosisCreate(BaseModel):
    crop_name: str
    disease_label: str
    confidence: float
    severity: str
    visible_symptoms: str
    likely_cause: str
    treatment: str
    preventive_measures: str
    plain_language_advisory: str
    language: str = "en"


def normalize_iso_timestamp(value: str) -> str:
    if value.endswith("Z"):
        return value.replace("Z", "+00:00")
    return value


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
    label = f"{crop} — Needs Expert Review"
    return {"label": label, "confidence": 0.35, "provider": "fallback"}


def fallback_advisory(
    crop_name: str, disease_label: str, confidence: float, language: str
) -> Dict[str, Any]:
    severity = severity_from_label(disease_label, confidence)
    crop = crop_name or "the crop"

    english = {
        "visible_symptoms": (
            f"Based on the current analysis, {crop} may show discoloration, spotting, "
            "wilting, or patchy damage on the leaves."
        ),
        "likely_cause": (
            "This result was generated using the fallback advisory mode. The issue may be "
            "caused by a fungal, bacterial, viral, pest, or nutrient-related problem."
        ),
        "severity": severity,
        "treatment": (
            "• Remove badly affected leaves if possible.\n"
            "• Avoid overwatering and improve airflow around the plant.\n"
            "• Consult a local agriculture expert before applying any chemical treatment."
        ),
        "preventive_measures": (
            "• Use clean tools and disease-free seeds.\n"
            "• Monitor leaves regularly for new symptoms.\n"
            "• Water near the soil instead of wetting leaves."
        ),
        "plain_language_advisory": (
            f"The system detected '{disease_label}' with limited model support. "
            "Treat this as an early warning and confirm with a local expert if symptoms worsen."
        ),
        "provider": "fallback",
    }

    hindi = {
        "visible_symptoms": "पत्तियों पर धब्बे, रंग बदलना, मुरझाना या असमान नुकसान दिखाई दे सकता है।",
        "likely_cause": "यह फॉलबैक सलाह है। समस्या फफूंद, बैक्टीरिया, वायरस, कीट या पोषण की कमी से जुड़ी हो सकती है।",
        "severity": severity,
        "treatment": "• बहुत प्रभावित पत्तियों को हटाएं।\n• अधिक पानी देने से बचें।\n• दवा उपयोग से पहले स्थानीय कृषि विशेषज्ञ से सलाह लें।",
        "preventive_measures": "• साफ औजारों का उपयोग करें।\n• पत्तियों की नियमित जांच करें।\n• पानी जड़ों के पास दें, पत्तियों पर नहीं।",
        "plain_language_advisory": f"सिस्टम ने '{disease_label}' का संकेत दिया है। इसे शुरुआती चेतावनी मानें और लक्षण बढ़ने पर विशेषज्ञ से पुष्टि करें।",
        "provider": "fallback",
    }

    marathi = {
        "visible_symptoms": "पानांवर डाग, रंग बदलणे, कोमेजणे किंवा असमान नुकसान दिसू शकते.",
        "likely_cause": "ही फॉलबॅक सल्ला प्रणाली आहे. समस्या बुरशी, जिवाणू, विषाणू, किडी किंवा पोषणअभावामुळे असू शकते.",
        "severity": severity,
        "treatment": "• जास्त बाधित पाने काढा.\n• जास्त पाणी देणे टाळा.\n• औषध वापरण्यापूर्वी स्थानिक कृषी तज्ञांचा सल्ला घ्या.",
        "preventive_measures": "• स्वच्छ साधने वापरा.\n• पानांची नियमित तपासणी करा.\n• पानांवर नाही तर मुळांजवळ पाणी द्या.",
        "plain_language_advisory": f"सिस्टमने '{disease_label}' असा इशारा दिला आहे. हे प्राथमिक सूचनास्वरूप समजा आणि लक्षणे वाढल्यास तज्ञांकडून खात्री करून घ्या.",
        "provider": "fallback",
    }

    return {"en": english, "hi": hindi, "mr": marathi}.get(language, english)


def classify_with_huggingface(image_bytes: bytes) -> Dict[str, Any]:
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is not configured")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(HF_MODEL_URL, headers=headers, data=image_bytes, timeout=30)
    response.raise_for_status()
    predictions = response.json()

    if isinstance(predictions, list) and predictions:
        top_pred = predictions[0]
        formatted_label = (
            top_pred["label"].replace("___", " — ").replace("_", " ").title()
        )
        return {
            "label": formatted_label,
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
- "label": The disease name in format "CropName — DiseaseName" (e.g., "Tomato — Early Blight"). If healthy, use "CropName — Healthy"
- "confidence": A float between 0.0 and 1.0 representing your confidence

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
- "severity": One of "Healthy", "Mild", "Moderate", or "Severe" (string, always in English)
- "treatment": Treatment steps as a single string with bullet points
- "preventive_measures": Prevention steps as a single string with bullet points
- "plain_language_advisory": Simple farmer advice in 2-3 sentences (string)

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


def prepare_status_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for record in records:
        if isinstance(record.get("timestamp"), str):
            record["timestamp"] = datetime.fromisoformat(
                normalize_iso_timestamp(record["timestamp"])
            )
    return records


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("CropSense AI backend started")
    logger.info("Storage mode: %s", storage.mode)


@app.get("/health")
async def root_health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "CropSense AI Backend",
        "timestamp": now_iso(),
        "storage": storage.health(),
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
    return await root_health_check()


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input_data: StatusCheckCreate) -> StatusCheck:
    status_obj = StatusCheck(**input_data.model_dump())
    payload = status_obj.model_dump()
    payload["timestamp"] = payload["timestamp"].isoformat()
    storage.insert_status_check(payload)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks() -> List[StatusCheck]:
    return prepare_status_records(storage.list_status_checks())


@api_router.post("/classify", response_model=ClassificationResponse)
async def classify_disease(
    file: UploadFile = File(...), crop_name: str = Form(default="Unknown")
) -> ClassificationResponse:
    image_bytes = await file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    providers = (
        lambda: classify_with_huggingface(image_bytes),
        lambda: classify_with_groq(image_base64, crop_name),
        lambda: fallback_classification(crop_name),
    )

    last_error = None
    for provider in providers:
        try:
            result = provider()
            logger.info(
                "Classification completed using %s", result.get("provider", "unknown")
            )
            return ClassificationResponse(**result)
        except Exception as exc:
            last_error = exc
            logger.warning("Classification provider failed: %s", exc)

    raise HTTPException(
        status_code=500,
        detail=f"Classification failed: {last_error}",
    )


@api_router.post("/advisory", response_model=AdvisoryResponse)
async def get_advisory(request: AdvisoryRequest) -> AdvisoryResponse:
    lang = request.language or "en"

    try:
        advisory_data = get_advisory_from_groq(
            request.crop_name, request.disease_label, request.confidence, lang
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
                lang,
            )
        )


@api_router.post("/history", response_model=DiagnosisRecord)
async def save_diagnosis(input_data: DiagnosisCreate) -> DiagnosisRecord:
    record = DiagnosisRecord(**input_data.model_dump())
    storage.insert_diagnosis(record.model_dump())
    return record


@api_router.get("/history", response_model=List[DiagnosisRecord])
async def get_history() -> List[DiagnosisRecord]:
    return storage.list_diagnoses(limit=50)


@api_router.delete("/history/{record_id}")
async def delete_diagnosis(record_id: str) -> Dict[str, str]:
    deleted = storage.delete_diagnosis(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Diagnosis record deleted"}


@api_router.delete("/history")
async def clear_history() -> Dict[str, str]:
    storage.clear_diagnoses()
    return {"message": "All history cleared"}


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
