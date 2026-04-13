# CropSense AI — Product Requirements Document

## Original Problem Statement
Build a complete React web app called "CropSense AI" — an AI-powered crop leaf disease detector for farmers. Features a stunning marketing landing page and a functional disease detection tool with HuggingFace ML model and Claude AI advisory.

## Architecture
- **Frontend**: React (CRA) + Tailwind CSS + Lucide Icons
- **Backend**: FastAPI + Python
- **Database**: MongoDB
- **Disease Classification**: Groq API (Llama 4 Scout vision model) as primary, HuggingFace (MobileNetV2) as first-try
- **Treatment Advisory**: Claude AI (Emergent LLM key) as primary, Groq as fallback

## User Personas
- **Farmers**: Upload leaf photos for instant disease diagnosis
- **Agricultural students**: Learn about plant diseases
- **Agronomists**: Quick field-level assessments

## Core Requirements (Static)
1. Landing page with hero, stats, how it works, pipeline, footer
2. App page with drag-drop upload, crop selector, analyze button
3. Disease classification via AI vision model
4. Treatment advisory via LLM
5. Results panel with severity badge, confidence, symptoms, cause, treatment, prevention, farmer advisory
6. Responsive design (mobile + desktop)

## What's Been Implemented (Feb 2026)
- [x] Landing page with all sections (Hero, Stats, How It Works, Pipeline, Footer)
- [x] App page with upload panel, crop selector (7 crops), analyze flow
- [x] Results panel with disease name, severity badge, confidence bar, 4-panel grid
- [x] Farmer advisory box with plain-language recommendations
- [x] Backend: /api/classify (Groq vision + HuggingFace fallback)
- [x] Backend: /api/advisory (Claude AI + Groq fallback)
- [x] Responsive design with Nunito font + organic green color palette
- [x] 3-step progress indicator during analysis
- [x] README.md with complete documentation

## Prioritized Backlog
### P0 (Critical)
- All core features implemented ✅

### P1 (Important)
- Multi-language advisory (Hindi, Marathi)
- Historical analysis tracking (save past diagnoses)
- Image quality validation before upload

### P2 (Nice to have)
- PWA / offline mode
- Mobile app version
- Share diagnosis results
- Batch image analysis
- Community forum for farmers

## Next Tasks
1. Deploy to GitHub (user's repo: github.com/rwitankar-byte/Harvest_health)
2. Add analysis history stored in MongoDB
3. Multi-language support
4. Image quality validation
