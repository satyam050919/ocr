from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import psycopg
import os
from dotenv import load_dotenv

from app.routers import document, processing

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Textract Document Processor API",
    description="API for processing documents using AWS Textract OCR",
    version="1.0.0",
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(document.router)
app.include_router(processing.router)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Textract Document Processor API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "version": app.version,
    }
