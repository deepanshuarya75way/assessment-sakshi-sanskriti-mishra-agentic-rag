"""
LangGraph-based RAG Pipeline with State Management & Latency Tracking
"""

from typing import Annotated, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_ollama import OllamaLLM
from vector_store import search_documents
import json
import re
import time
from typing_extensions import TypedDict

# ============================================
# State Definition
# ============================================

class RAGState(TypedDict):
    """State management for RAG pipeline"""
    query: str
    messages: list[BaseMessage]
    route: Literal["rag", "direct", "math"]
    context: str
    sources: list[str]
    answer: dict
    relevance_score: float
    timings: dict  # Add timing tracking


# ============================================
# LLM Configuration
# ============================================

llm = OllamaLLM(
    model="phi",  # Faster model: 2.7B parameters (was llama3: 8B)
    temperature=0.3,
    top_p=0.9,
)


# ============================================
# Node Functions
# ============================================

def analyze_query(state: RAGState) -> RAGState:
    """
    Analyze query and determine routing
    """
    start_time = time.time()
    query = state["query"].lower()
    
    # Math detection
    if any(op in query for op in ['+', '-', '*', '/', '=', '**']) or any(
        keyword in query for keyword in ['calculate', 'math', 'sum', 'multiply', 'divide', 'equals']
    ):
        state["route"] = "math"
        state["timings"]["analyze"] = time.time() - start_time
        print(f"🧮 Routed to: MATH ({state['timings']['analyze']:.3f}s)")
        return state
    
    # Direct LLM queries (knowledge, time, definitions)
    direct_keywords = ['what is', 'who is', 'when', 'where', 'how', 'why', 'tell me', 'explain', 
                       'define', 'meaning', 'time', 'date', 'today', 'now', 'current']
    
    if any(keyword in query for keyword in direct_keywords):
        state["route"] = "direct"
        state["timings"]["analyze"] = time.time() - start_time
        print(f"🤖 Routed to: DIRECT LLM ({state['timings']['analyze']:.3f}s)")
        return state
    
    # Default to RAG
    state["route"] = "rag"
    state["timings"]["analyze"] = time.time() - start_time
    print(f"📚 Routed to: RAG ({state['timings']['analyze']:.3f}s)")
    return state


def retrieve_context(state: RAGState) -> RAGState:
    """
    Retrieve relevant documents
    """
    start_time = time.time()
    
    if state["route"] == "rag":
        results = search_documents(state["query"], top_k=3)
        
        if len(results.points) > 0:
            relevance = results.points[0].score
            state["relevance_score"] = relevance
            print(f"   Top Relevance Score: {relevance:.4f}")
            
            # Check if relevance is too low
            if relevance < 0.55:
                print(f"   ⚠️ Score too low, falling back to LLM")
                state["route"] = "direct"
                state["timings"]["retrieve"] = time.time() - start_time
                return state
            
            # Extract context and sources
            context_chunks = []
            sources = set()
            
            for hit in results.points[:2]:
                if "text" in hit.payload:
                    context_chunks.append(hit.payload["text"])
                if "source" in hit.payload:
                    sources.add(hit.payload["source"])
            
            state["context"] = "\n---\n".join(context_chunks)
            state["sources"] = list(sources)
        else:
            state["route"] = "direct"
    
    state["timings"]["retrieve"] = time.time() - start_time
    print(f"   Retrieval time: {state['timings']['retrieve']:.3f}s")
    return state


def build_math_answer(state: RAGState) -> RAGState:
    """
    Handle math queries
    """
    start_time = time.time()
    
    prompt = f"""Calculate this math problem: {state['query']}

Respond ONLY in JSON format:
{{"summary": "The answer", "details": "Step-by-step solution", "key_points": ["step1", "step2"]}}

Example for 2+2:
{{"summary": "2 + 2 = 4", "details": "Two plus two equals four", "key_points": ["2", "+", "2", "=", "4"]}}

Answer:"""
    
    llm_start = time.time()
    response = llm.invoke(prompt)
    state["timings"]["llm_invoke"] = time.time() - llm_start
    
    state["answer"] = parse_response(response)
    
    state["timings"]["math"] = time.time() - start_time
    print(f"   Math generation: {state['timings']['math']:.3f}s (LLM: {state['timings']['llm_invoke']:.3f}s)")
    return state


def build_direct_answer(state: RAGState) -> RAGState:
    """
    Generate answer without document context
    """
    start_time = time.time()
    
    prompt = f"""Answer this question directly:
{state['query']}

Respond ONLY in JSON format:
{{"summary": "1-2 sentence answer", "details": "Detailed explanation", "key_points": ["point1", "point2", "point3"]}}

Make sure it's valid JSON:"""
    
    llm_start = time.time()
    response = llm.invoke(prompt)
    state["timings"]["llm_invoke"] = time.time() - llm_start
    
    state["answer"] = parse_response(response)
    
    state["timings"]["direct"] = time.time() - start_time
    print(f"   Direct LLM: {state['timings']['direct']:.3f}s (LLM: {state['timings']['llm_invoke']:.3f}s)")
    return state


def build_rag_answer(state: RAGState) -> RAGState:
    """
    Generate answer from document context
    """
    start_time = time.time()
    
    prompt = f"""You are an expert AI assistant. Answer ONLY based on the provided context.

IMPORTANT: Respond in this EXACT JSON format:
{{
    "summary": "1-2 sentence concise answer",
    "details": "Clear, detailed explanation",
    "key_points": ["point 1", "point 2", "point 3"]
}}

Context:
{state['context']}

Question: {state['query']}

Rules:
1. Be concise and direct
2. If not in context: {{"summary": "Not found", "details": "", "key_points": []}}
3. RESPOND ONLY WITH VALID JSON:"""
    
    llm_start = time.time()
    response = llm.invoke(prompt)
    state["timings"]["llm_invoke"] = time.time() - llm_start
    
    state["answer"] = parse_response(response)
    
    state["timings"]["rag"] = time.time() - start_time
    print(f"   RAG generation: {state['timings']['rag']:.3f}s (LLM: {state['timings']['llm_invoke']:.3f}s)")
    return state


def route_to_generation(state: RAGState) -> str:
    """
    Route to appropriate answer generation
    """
    return state["route"]


# ============================================
# Helper Functions
# ============================================

def parse_response(response_text: str) -> dict:
    """
    Extract JSON from LLM response
    """
    try:
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            if "summary" in parsed:
                return parsed
    except Exception as e:
        print(f"JSON parse error: {e}")
    
    # Fallback
    return {
        "summary": response_text[:150],
        "details": response_text,
        "key_points": []
    }


# ============================================
# LangGraph Workflow
# ============================================

def create_rag_graph():
    """
    Create LangGraph workflow
    """
    from langgraph.graph import StateGraph, END
    
    # Create graph
    workflow = StateGraph(RAGState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_query)
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("math", build_math_answer)
    workflow.add_node("direct", build_direct_answer)
    workflow.add_node("rag", build_rag_answer)
    
    # Set entry point
    workflow.set_entry_point("analyze")
    
    # Add edges
    workflow.add_edge("analyze", "retrieve")
    
    # Conditional routing from retrieve
    def route_after_retrieve(state: RAGState) -> str:
        return state["route"]
    
    workflow.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "math": "math",
            "direct": "direct",
            "rag": "rag",
        }
    )
    
    # All generation nodes lead to END
    workflow.add_edge("math", END)
    workflow.add_edge("direct", END)
    workflow.add_edge("rag", END)
    
    # Compile
    return workflow.compile()


# ============================================
# Main Functions
# ============================================

def generate_answer_graph(query: str) -> dict:
    """
    Generate answer using LangGraph
    """
    total_start = time.time()
    graph = create_rag_graph()
    
    # Initial state
    initial_state = RAGState(
        query=query,
        messages=[],
        route="rag",
        context="",
        sources=[],
        answer={},
        relevance_score=0.0,
        timings={}
    )
    
    # Run graph
    final_state = graph.invoke(initial_state)
    
    total_time = time.time() - total_start
    final_state["timings"]["total"] = total_time
    
    # Log detailed timings
    print("\n" + "="*60)
    print("⏱️ LATENCY BREAKDOWN:")
    print("="*60)
    for key, value in final_state["timings"].items():
        if key != "total":
            percentage = (value / total_time) * 100
            print(f"  {key:.<30} {value:>6.3f}s ({percentage:>5.1f}%)")
    print("-"*60)
    print(f"  {'TOTAL':.<30} {total_time:>6.3f}s (100.0%)")
    print("="*60 + "\n")
    
    return {
        "question": query,
        "answer": final_state["answer"],
        "sources": final_state["sources"],
        "route": final_state["route"],
        "relevance_score": final_state["relevance_score"],
        "timings": final_state["timings"]
    }


if __name__ == "__main__":
    # Test
    result = generate_answer_graph("What is machine learning?")
    print("\nRESULT:")
    print(json.dumps({k: v for k, v in result.items() if k != "timings"}, indent=2))
