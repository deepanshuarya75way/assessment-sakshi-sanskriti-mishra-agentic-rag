import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import get_settings
from langgraph_rag import generate_answer_graph


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title="Agentic RAG API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4_000)


class AnswerDetail(BaseModel):
    summary: str
    details: str = ""
    key_points: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    question: str
    answer: AnswerDetail
    sources: list[str] = Field(default_factory=list)
    route: str
    relevance_score: float = 0.0
    timings: dict[str, float] = Field(default_factory=dict)


@app.get("/", tags=["Health"])
def home():
    return {"status": "ok", "message": "Agentic RAG API is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question cannot be empty.")
    try:
        return generate_answer_graph(question)
    except RuntimeError as error:
        logger.warning("Chat request could not be completed: %s", error)
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception:
        logger.exception("Unexpected error while processing chat request")
        raise HTTPException(status_code=500, detail="Unable to process the question.")


@app.post("/debug/route", tags=["Debug"])
def debug_route(request: ChatRequest):
    response = chat(request)
    return {
        "question": response["question"],
        "route": response["route"],
        "relevance_score": response["relevance_score"],
        "sources": response["sources"],
        "timings": response["timings"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
