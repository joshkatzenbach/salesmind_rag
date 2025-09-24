"""
SalesMind RAG API - Main application file.
"""

import os

# Set environment to production if not already set (for Render deployment)
if not os.getenv("ENVIRONMENT"):
    os.environ["ENVIRONMENT"] = "production"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import general_endpoints, transcript_endpoints, query_endpoints, auth_endpoints, user_management_endpoints, prompt_history_endpoints

# FastAPI app
app = FastAPI(title="SalesMind RAG API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",   # Angular dev
        "https://salesmind-rag.firebaseapp.com",
        "https://salesmind-rag.web.app",
        "https://salesmind.coach"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(general_endpoints.router)
app.include_router(auth_endpoints.router)
app.include_router(transcript_endpoints.router)
app.include_router(query_endpoints.router)
app.include_router(user_management_endpoints.router)
app.include_router(prompt_history_endpoints.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)