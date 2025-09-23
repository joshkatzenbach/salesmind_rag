"""
SalesMind RAG API - Main application file.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import general_endpoints, transcript_endpoints, query_endpoints, auth_endpoints

# FastAPI app
app = FastAPI(title="SalesMind RAG API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",   # Angular dev
        "https://https://salesmind-rag.firebaseapp.com",
        "https://salesmind-rag.web.app",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)