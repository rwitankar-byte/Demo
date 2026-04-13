# 🌿 CropSense AI — Leaf Disease Detector

> **FOAI Group Project** · AI-Powered Crop Disease Detection & Farm Advisory System

![Model Accuracy](https://img.shields.io/badge/Model%20Accuracy-95.41%25-brightgreen)
![HuggingFace](https://img.shields.io/badge/HuggingFace-MobileNetV2-orange)
![Claude AI](https://img.shields.io/badge/Advisory-Claude%20AI-blueviolet)
![Classes](https://img.shields.io/badge/Disease%20Classes-38-blue)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

---

## 📌 What is CropSense AI?

CropSense AI is a web-based tool that lets farmers upload a photo of a leaf and instantly get:

- ✅ Disease identification (from 38 known plant diseases)
- ✅ Model confidence score
- ✅ Visible symptoms & likely cause
- ✅ Treatment & prevention steps
- ✅ Plain-language farmer advisory (powered by Claude AI)

The goal is to make expert-level crop diagnosis accessible to any farmer with a phone — no jargon, no searching required.

---

## 🧠 How the Pipeline Works

```
Farmer uploads photo
      ↓
HuggingFace API (MobileNetV2 · 38 classes)
      ↓
Disease label + confidence score (95.41% accuracy)
      ↓
Claude AI (treatment + plain-language advisory)
      ↓
Result shown on screen (~5 seconds total)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Tailwind CSS, Lucide Icons |
| Backend | FastAPI, Python |
| Database | MongoDB |
| Disease Classification | HuggingFace Inference API |
| ML Model | `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification` |
| Advisory Generation | Anthropic Claude API (`claude-sonnet-4-20250514`) |
| Fonts | Nunito (Google Fonts) |
| Hosting | Emergent Platform |

---

## 🌾 Supported Crops

Tomato · Potato · Wheat · Corn · Apple · Pepper · and more

The model covers **38 plant disease classes** across multiple crop types. Selecting your crop helps Claude generate a more targeted advisory.

---

## 📂 Project Structure

```
cropsense-ai/
├── backend/
│   ├── server.py          # FastAPI backend with HF & Claude integration
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Landing & App pages
│   │   ├── App.js        # Main app with routing
│   │   └── index.css     # Global styles with design system
│   └── package.json      # Node dependencies
└── README.md             # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and Yarn
- Python 3.9+
- MongoDB

### Run Locally

```bash
# Clone the repository
git clone https://github.com/rwitankar-byte/Harvest_health.git
cd Harvest_health

# Backend setup
cd backend
pip install -r requirements.txt
# Add your API keys to .env file
uvicorn server:app --reload --port 8001

# Frontend setup (in new terminal)
cd frontend
yarn install
yarn start
```

### Environment Variables

**Backend (.env):**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=cropsense_db
CORS_ORIGINS=*
EMERGENT_LLM_KEY=your_emergent_key_here
HF_TOKEN=your_huggingface_token_here
```

**Frontend (.env):**
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

### API Keys Required

The app uses two external APIs:

1. **HuggingFace API Token** — for the disease classification model
   - Get one at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Set `HF_TOKEN` in backend/.env

2. **Emergent LLM Key** — for Claude-powered advisory
   - Available through Emergent Platform
   - Set `EMERGENT_LLM_KEY` in backend/.env
   - Alternatively, use your own Anthropic API key

---

## 🎯 Features

- **Drag & drop** or click-to-upload leaf image
- **Live preview** of uploaded image
- **Crop selector** (7 crop types) to improve advisory accuracy
- **3-step progress indicator** during analysis
- **Confidence bar** showing model certainty
- **Severity badge** — Healthy / Mild / Moderate / Severe
- **4-panel info grid** — Symptoms, Cause, Treatment, Prevention
- **Farmer advisory box** — plain-language action steps
- Fully **responsive** (mobile + desktop)
- **Vibrant & farmer-friendly** design with organic color palette

---

## 👥 Team & Roles

| Member | Role |
|---|---|
| Member 1 | ML Model & HuggingFace Integration |
| **Member 2 (you)** | **Website Lead — Frontend & API Integration** |
| Member 3 | Claude AI Prompting & Advisory Design |
| Member 4 | Testing, Docs & Deployment |

> Update this table with real names before submitting.

---

## 📊 Model Details

- **Model:** `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`
- **Architecture:** MobileNetV2
- **Dataset:** PlantVillage (38 disease classes)
- **Accuracy:** 95.41%
- **Inference:** HuggingFace Inference API (serverless)

---

## 🗺️ Roadmap

- [x] Upload & preview leaf image
- [x] HuggingFace disease classification
- [x] Claude AI advisory generation
- [x] Responsive UI with progress steps
- [x] Landing page with vibrant farmer-friendly design
- [ ] Multi-language advisory (Hindi, Marathi)
- [ ] Offline mode / PWA support
- [ ] Mobile app version
- [ ] Historical analysis tracking

---

## 📸 Screenshots

> Add screenshots here once deployed.

---

## 📄 License

This project is built for academic purposes as part of the **FOAI (Foundations of AI)** course group project.

---

<div align="center">
  Built with 🌱 by the CropSense AI Team &nbsp;·&nbsp; FOAI Group Project
</div>
