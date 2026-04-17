"""
Render Health Check - Add to your backend to prevent spin-down
This endpoint keeps the backend alive by responding to periodic pings
"""

# Add this to your FastAPI server (backend/server.py)

@app.get("/health")
async def health_check():
    """Health check endpoint to prevent Render instance from spinning down"""
    return {
        "status": "healthy",
        "service": "CropSense AI Backend",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Optional: Add startup event to log when service starts
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 CropSense AI Backend Started")
    logger.info(f"MongoDB: {os.environ.get('DB_NAME')}")


# Then go to Render Dashboard:
# 1. Settings → Health Check
# 2. Check "Enable"
# 3. Health Check Path: /health
# 4. Check Interval: 5 min
# 5. Save
