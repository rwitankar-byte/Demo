# 🌿 CropSense AI — Leaf Disease Detector

> **FOAI Group Project** · AI-Powered Crop Disease Detection & Farm Advisory System

Live frontend: [demo-frontend-f5dn.onrender.com](https://demo-frontend-f5dn.onrender.com)

![Model Accuracy](https://img.shields.io/badge/Model%20Accuracy-95.41%25-brightgreen)
![HuggingFace](https://img.shields.io/badge/HuggingFace-MobileNetV2-orange)
![Groq AI](https://img.shields.io/badge/Advisory-Groq%20AI-blueviolet)
![Classes](https://img.shields.io/badge/Disease%20Classes-38-blue)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

---

## 📌 What is CropSense AI?

CropSense AI is a web-based tool that lets farmers upload a photo of a leaf and instantly get:

- ✅ Disease identification (from 38 known plant diseases)
- ✅ Model confidence score
- ✅ Visible symptoms & likely cause
- ✅ Treatment & prevention steps
- ✅ Plain-language farmer advisory (powered by Groq AI)

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
Groq AI (treatment + plain-language advisory)
      ↓
Result shown on screen (~5 seconds total)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Tailwind CSS, Lucide Icons |
| Backend | FastAPI, Python |
| Database | None (stateless setup) |
| Disease Classification | HuggingFace Inference API |
| ML Model | `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification` |
| Advisory Generation | Groq API |
| Fonts | Nunito (Google Fonts) |
| Hosting | Render |

---

## 🌾 Supported Crops

Tomato · Potato · Wheat · Corn · Apple · Pepper · and more

The model covers **38 plant disease classes** across multiple crop types. Selecting your crop helps the advisory model generate more targeted guidance.

---

## 📂 Project Structure

```
cropsense-ai/
├── backend/
│   ├── server.py          # FastAPI backend with HF & Groq integration
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

- Node.js 20 LTS
- Python 3.11+

### Run Locally

```bash
# Clone the repository
git clone https://github.com/rwitankar-byte/Demo.git
cd Demo

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
CORS_ORIGINS=*
HF_TOKEN=your_huggingface_token_here
GROQ_API_KEY=your_groq_api_key_here
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

2. **Groq API Key** — for advisory generation
   - Set `GROQ_API_KEY` in backend/.env

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
- **No farmer data storage** in the current deployment design

---

## 👥 Team & Roles

| Member | Role |
|---|---|
| Ankan Mondal | ML Model & HuggingFace Integration |
| Rwitankar Pal | **Website Lead — Frontend & API Integration** |
| Naina Sharma | Advisory Prompting & Groq Integration |
| Amrisha | Testing, Docs & Deployment |

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
- [x] Groq AI advisory generation
- [x] Responsive UI with progress steps
- [x] Landing page with vibrant farmer-friendly design
- [ ] Multi-language advisory (Hindi, Marathi)
- [ ] Offline mode / PWA support
- [ ] Mobile app version
- [ ] Optional history tracking in a future version

---

## 📸 Screenshots

Live app: [demo-frontend-f5dn.onrender.com](https://demo-frontend-f5dn.onrender.com)

---

## 📄 License

This project is built for academic purposes as part of the **FOAI (Fundamentals of AI)** course group project.

---

<div align="center">
  Built with 🌱 by the NeuralFlare Team &nbsp;·&nbsp; FOAI Group Project
</div>
