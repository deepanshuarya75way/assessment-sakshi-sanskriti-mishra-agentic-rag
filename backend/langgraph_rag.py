import ast
import json
import logging
import operator
import re
import time
from typing import Literal

from langchain_ollama import OllamaLLM
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from config import get_settings
from vector_store import search_documents


logger = logging.getLogger(__name__)
RELEVANCE_THRESHOLD = 0.55


class RAGState(TypedDict):
    query: str
    route: Literal["rag", "direct", "math"]
    context: str
    sources: list[str]
    answer: dict
    relevance_score: float
    timings: dict


def _get_llm():
    settings = get_settings()
    options = {"model": settings.ollama_model, "temperature": 0.3}
    if settings.ollama_base_url:
        options["base_url"] = settings.ollama_base_url
    return OllamaLLM(**options)


def _parse_answer(response: str) -> dict:
    try:
        match = re.search(r"\{[\s\S]*\}", response)
        parsed = json.loads(match.group(0) if match else response)
        if isinstance(parsed, dict) and parsed.get("summary"):
            return {
                "summary": str(parsed["summary"]),
                "details": str(parsed.get("details", "")),
                "key_points": [str(point) for point in parsed.get("key_points", [])],
            }
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    return {"summary": response.strip()[:180], "details": response.strip(), "key_points": []}


def _invoke(prompt: str, timings: dict) -> dict:
    started = time.perf_counter()
    try:
        response = _get_llm().invoke(prompt)
    except Exception as error:
        raise RuntimeError("The Ollama service is unavailable. Start Ollama and pull the configured model.") from error
    timings["llm_invoke"] = time.perf_counter() - started
    return _parse_answer(response)


def analyze_query(state: RAGState):
    started = time.perf_counter()
    query = state["query"].strip()
    state["route"] = "math" if _extract_expression(query) else "rag"
    state["timings"]["analyze"] = time.perf_counter() - started
    return state


def retrieve_context(state: RAGState):
    started = time.perf_counter()
    if state["route"] != "rag":
        state["timings"]["retrieve"] = 0.0
        return state

    results = search_documents(state["query"])
    if results:
        state["relevance_score"] = results[0].score
        if results[0].score >= RELEVANCE_THRESHOLD:
            state["context"] = "\n\n---\n\n".join(hit.payload["text"] for hit in results[:2] if hit.payload.get("text"))
            state["sources"] = sorted({hit.payload["source"] for hit in results[:2] if hit.payload.get("source")})
        else:
            state["route"] = "direct"
    else:
        state["route"] = "direct"
    state["timings"]["retrieve"] = time.perf_counter() - started
    return state


def build_rag_answer(state: RAGState):
    started = time.perf_counter()
    state["answer"] = _invoke(
        f"""Answer the question using only the supplied context. If the answer is absent, say so clearly.

Context:
{state['context']}

Question: {state['query']}

Return valid JSON only: {{\"summary\": \"concise answer\", \"details\": \"explanation\", \"key_points\": [\"point\"]}}""",
        state["timings"],
    )
    state["timings"]["generate"] = time.perf_counter() - started
    return state


def build_direct_answer(state: RAGState):
    started = time.perf_counter()
    state["answer"] = _invoke(
        f"""Answer this question clearly. Return valid JSON only:
{{\"summary\": \"concise answer\", \"details\": \"explanation\", \"key_points\": [\"point\"]}}

Question: {state['query']}""",
        state["timings"],
    )
    state["timings"]["generate"] = time.perf_counter() - started
    return state


_OPERATORS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow}


def _extract_expression(query: str):
    match = re.fullmatch(r"\s*(?:calculate\s+)?([0-9+\-*/().\s]+)\s*", query, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    raise ValueError("Unsupported expression")


def build_math_answer(state: RAGState):
    started = time.perf_counter()
    expression = _extract_expression(state["query"])
    try:
        result = _evaluate(ast.parse(expression, mode="eval").body)
        state["answer"] = {"summary": f"{expression.strip()} = {result}", "details": "Calculated locally.", "key_points": []}
    except (SyntaxError, ValueError, ZeroDivisionError):
        state["answer"] = {"summary": "I couldn't evaluate that expression.", "details": "Use a basic arithmetic expression such as 2 + 2.", "key_points": []}
    state["timings"]["generate"] = time.perf_counter() - started
    return state


def create_rag_graph():
    workflow = StateGraph(RAGState)
    workflow.add_node("analyze", analyze_query)
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("rag", build_rag_answer)
    workflow.add_node("direct", build_direct_answer)
    workflow.add_node("math", build_math_answer)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "retrieve")
    workflow.add_conditional_edges("retrieve", lambda state: state["route"], {"rag": "rag", "direct": "direct", "math": "math"})
    workflow.add_edge("rag", END)
    workflow.add_edge("direct", END)
    workflow.add_edge("math", END)
    return workflow.compile()


def generate_answer_graph(query: str):
    started = time.perf_counter()
    state = create_rag_graph().invoke({
        "query": query,
        "route": "rag",
        "context": "",
        "sources": [],
        "answer": {},
        "relevance_score": 0.0,
        "timings": {},
    })
    state["timings"]["total"] = time.perf_counter() - started
    return {key: state[key] for key in ("answer", "sources", "route", "relevance_score", "timings")} | {"question": query}
