from langchain_ollama import OllamaLLM
from vector_store import search_documents
import json
import re

# Load Llama3 - optimized settings
llm = OllamaLLM(
    model="llama3",
    temperature=0.3,
    top_p=0.9,
)

# Constants
RELEVANCE_THRESHOLD = 0.55
MAX_CONTEXT_CHUNKS = 2  # Limit to top 2 for speed


def route_query(query):
    """
    Decide whether to use RAG or Direct LLM
    """
    # List of queries that should NOT use RAG
    non_rag_keywords = [
        # Math
        '+', '-', '*', '/', '=', '**', 'calculate', 'math', 'equals', 'sum', 'multiply', 'divide',
        # General knowledge
        'what is', 'who is', 'when', 'where', 'how', 'why', 'tell me', 'explain', 'define',
        'meaning', 'definition', 'what does',
        # Time/Current
        'time', 'date', 'today', 'now', 'current',
    ]
    
    query_lower = query.lower()
    
    # Check if query should skip RAG
    for keyword in non_rag_keywords:
        if keyword in query_lower:
            # Still search, but with lower threshold
            results = search_documents(query, top_k=3)
            if len(results.points) > 0:
                top_score = results.points[0].score
                print(f"Top Score for '{query}': {top_score:.4f}")
                
                # Only use RAG if score is VERY high (0.7+)
                if top_score >= 0.7:
                    return "rag", results
            
            return "llm", None
    
    # For normal queries, use standard routing
    results = search_documents(query, top_k=3)

    if len(results.points) == 0:
        return "llm", None

    top_score = results.points[0].score
    print(f"Top Score: {top_score:.4f}")

    if top_score >= 0.55:
        return "rag", results

    return "llm", None


def build_prompt(query, context):
    """
    Build optimized RAG Prompt for structured output
    """

    prompt = f"""You are an expert AI assistant with deep knowledge. Answer ONLY based on the provided context.

IMPORTANT: Respond in this EXACT JSON format:
{{
    "summary": "1-2 sentence concise answer",
    "details": "Clear, detailed explanation (2-3 paragraphs)",
    "key_points": ["point 1", "point 2", "point 3"]
}}

Rules:
1. Be concise and direct
2. Use simple language
3. If answer not in context, respond: {{"summary": "Not found in documents", "details": "", "key_points": []}}

Context:
{context}

Question: {query}

RESPOND ONLY WITH VALID JSON, NO OTHER TEXT:"""

    return prompt


def parse_response(response_text):
    """
    Extract and parse JSON from response
    """
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            # Ensure all required fields exist
            if "summary" in parsed:
                return parsed
    except Exception as e:
        print(f"JSON parse error: {e}")
    
    # Fallback if parsing fails - convert plain text to structured format
    text = response_text.strip()
    return {
        "summary": text[:150],
        "details": text,
        "key_points": []
    }


def direct_llm_answer(query):
    """
    Direct LLM without retrieval - optimized for math and simple queries
    """

    # Simple check for math questions
    if any(op in query for op in ['+', '-', '*', '/', '=', '**']):
        prompt = f"""Calculate this: {query}

Respond ONLY with the calculation and result in this JSON format:
{{"summary": "The answer", "details": "Step-by-step explanation", "key_points": []}}

Example:
{{"summary": "2+2 = 4", "details": "Two plus two equals four", "key_points": []}}

Now answer:"""
    else:
        prompt = f"""You are a helpful AI assistant.

Answer this question:
{query}

Respond in JSON format:
{{"summary": "brief answer (1 sentence)", "details": "detailed explanation", "key_points": ["point1", "point2"]}}

Make sure response is ONLY valid JSON, nothing else:"""

    response = llm.invoke(prompt)
    print(f"Direct LLM Response: {response[:200]}")
    return parse_response(response)


def rag_answer(query, results):
    """
    Generate answer using retrieved documents (optimized for speed)
    """

    context_chunks = []
    sources = set()

    # Use only top MAX_CONTEXT_CHUNKS for faster processing
    for hit in results.points[:MAX_CONTEXT_CHUNKS]:
        if hit.score < RELEVANCE_THRESHOLD:
            continue

        if "text" in hit.payload:
            context_chunks.append(hit.payload["text"])

        if "source" in hit.payload:
            sources.add(hit.payload["source"])

    if not context_chunks:
        return parse_response(""), list(sources)

    # Limit context to reduce token count
    context = "\n---\n".join(context_chunks[:MAX_CONTEXT_CHUNKS])

    prompt = build_prompt(query, context)

    answer = llm.invoke(prompt)
    parsed_answer = parse_response(answer)

    return parsed_answer, list(sources)


def generate_answer(query):
    """
    Main Router
    """

    route, results = route_query(query)

    if route == "rag":

        answer, sources = rag_answer(query, results)

        return {
            "mode": "RAG",
            "question": query,
            "answer": answer,
            "sources": sources
        }

    else:

        answer = direct_llm_answer(query)

        return {
            "mode": "LLM",
            "question": query,
            "answer": answer,
            "sources": []
        }


def generate_answer(query):
    """
    Main Router
    """

    route, results = route_query(query)

    if route == "rag":

        answer, sources = rag_answer(query, results)

        return {
            "mode": "RAG",
            "question": query,
            "answer": answer,
            "sources": sources
        }

    else:

        answer = direct_llm_answer(query)

        return {
            "mode": "LLM",
            "question": query,
            "answer": answer,
            "sources": []
        }


if __name__ == "__main__":

    query = input("Enter your question: ")

    result = generate_answer(query)

    print("\n" + "=" * 60)
    print("MODE:")
    print(result["mode"])

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(result["question"])

    print("\n" + "=" * 60)
    print("ANSWER:")
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SOURCES:")

    if result["sources"]:
        for source in result["sources"]:
            print("-", source)
    else:
        print("No sources used (Direct LLM Mode)")