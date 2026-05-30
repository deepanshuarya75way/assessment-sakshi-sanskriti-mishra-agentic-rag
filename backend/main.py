from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import json

from langgraph_rag import generate_answer_graph

# ============================================
# Configuration
# ============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic RAG API",
    description="Retrieval-Augmented Generation API with LLM Integration",
    version="1.0.0"
)

# ============================================
# CORS Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Request/Response Models
# ============================================

class AnswerDetail(BaseModel):
    summary: str = ""
    details: str = ""
    key_points: List[str] = []


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: AnswerDetail
    sources: List[str]
    route: str = ""
    relevance_score: float = 0.0
    timings: dict = {}


# ============================================
# Routes
# ============================================

@app.get("/", tags=["Health"])
def home():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Agentic RAG API with LangGraph Running",
        "routing": "LangGraph with intelligent state management"
    }


@app.post("/chat", tags=["Chat"])
def chat(request: ChatRequest):
    """
    Query the RAG system with a question using LangGraph routing
    
    Returns:
    - question: The input question
    - answer: Structured answer with summary, details, and key points
    - sources: Document sources used for context
    - route: Which route was taken (math, direct, rag)
    - relevance_score: Relevance score from vector search
    - timings: Latency breakdown for each stage
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Processing query: {request.question}")
        result = generate_answer_graph(request.question)
        
        logger.info(f"Route used: {result['route']}, Score: {result['relevance_score']:.2f}")
        
        # Return as JSON directly to preserve all fields
        return JSONResponse(content={
            "question": result["question"],
            "answer": result["answer"],
            "sources": result["sources"],
            "route": result.get("route", "unknown"),
            "relevance_score": result.get("relevance_score", 0.0),
            "timings": result.get("timings", {})
        })
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug/route", tags=["Debug"])
def debug_route(request: ChatRequest):
    """
    Debug endpoint to see which route a query takes and all timings
    """
    try:
        result = generate_answer_graph(request.question)
        return {
            "question": request.question,
            "route": result["route"],
            "relevance_score": result["relevance_score"],
            "has_sources": len(result["sources"]) > 0,
            "sources": result["sources"],
            "timings": result.get("timings", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Startup Events
# ============================================

@app.on_event("startup")
async def startup_event():
    logger.info("API Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API Shutting down...")