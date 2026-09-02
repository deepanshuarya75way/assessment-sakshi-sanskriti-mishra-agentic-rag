import { useEffect, useRef, useState } from "react";
import Message from "./Message";
import { sendChatMessage } from "../services/api";
import "./ChatBox.css";

function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || isLoading) return;

    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError("");
    setIsLoading(true);

    try {
      const data = await sendChatMessage(question);
      const assistantMessage = {
        role: "assistant",
        text: {
          summary: data.answer?.summary || "Response",
          details: data.answer?.details || "",
          key_points: data.answer?.key_points || [],
          sources: data.sources || [],
        },
        timings: data.timings || {},
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (requestError) {
      setError(requestError.message || "Unable to reach the API.");
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-header">
        <div className="header-content">
          <h1 className="header-title">🤖 Agentic RAG Assistant</h1>
          <p className="header-subtitle">Powered by LangGraph & Vector Search</p>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && !isLoading && (
          <div className="empty-state">
            <h2>Ask your knowledge base</h2>
            <p>Try a document question, such as “What does the company policy say about leave?”</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <Message key={idx} role={msg.role} text={msg.text} timings={msg.timings} />
        ))}
        {error && <p className="request-error" role="alert">{error}</p>}
        {isLoading && (
          <div className="loading-container">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-section">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question... (Shift+Enter for new line)"
            className="input-field"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="send-button"
            title="Send message"
          >
            {isLoading ? (
              <span className="spinner"></span>
            ) : (
              <span className="send-icon">➤</span>
            )}
          </button>
        </div>
        <p className="input-hint">💡 Use natural language to query documents</p>
      </div>

      <div className="footer">
        <p>Agentic RAG © 2024</p>
      </div>
    </div>
  );
}

export default ChatBox;
