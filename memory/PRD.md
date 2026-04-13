# CropSense AI — Product Requirements Document

## Original Problem Statement
Build a complete React web app called "CropSense AI" — an AI-powered crop leaf disease detector for farmers.

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Lucide Icons
- **Backend**: FastAPI + Python
- **Database**: MongoDB (diagnoses collection for history)
- **Disease Classification**: Groq API (Llama 4 Scout vision) primary, HuggingFace (MobileNetV2) first-try
- **Treatment Advisory**: Claude AI (Emergent LLM key) primary, Groq fallback
- **Multi-language**: Hindi (हिन्दी), Marathi (मराठी) via LLM translation

## User Personas
- Farmers: Upload leaf photos for disease diagnosis in local languages
- Agricultural students: Learn about plant diseases
- Agronomists: Quick field assessments with shareable reports

## What's Been Implemented (Feb-Apr 2026)

### Phase 1 (MVP)
- [x] Landing page with Hero, Stats, How It Works, Pipeline, Footer
- [x] App page with drag-drop upload, crop selector, analyze flow
- [x] Disease classification via Groq Vision + HuggingFace
- [x] Treatment advisory via Claude AI + Groq fallback
- [x] Results panel with severity, confidence, 4-panel grid, farmer advisory

### Phase 2 (New Features)
- [x] Analysis history — auto-saved to MongoDB, viewable at /history
- [x] History page — list + detail panel, delete/clear functionality
- [x] Multi-language — English, Hindi, Marathi advisory generation
- [x] WhatsApp Share — one-click share diagnosis to WhatsApp
- [x] Language badge on results and history

## Prioritized Backlog
### P1
- Offline mode / PWA support
- Image quality validation before upload
- Export history as PDF report

### P2
- Mobile app version
- Batch image analysis
- Community forum for farmers
- Weather-based disease alerts

## Next Tasks
1. Add more languages (Tamil, Telugu, Bengali)
2. PDF export for diagnosis reports
3. PWA offline mode
