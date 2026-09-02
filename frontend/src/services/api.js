const apiBaseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function sendChatMessage(question) {
  const response = await fetch(`${apiBaseUrl}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(payload?.detail || `Request failed with status ${response.status}.`);
  }

  return payload;
}
