import { useState } from "react";
import axios from "axios";
import Message from "./Message";

function ChatBox() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useState(null);

  const scrollToBottom = () => {
    setTimeout(() => {
      const container = document.querySelector('[data-messages-container]');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 100);
  };

  const sendMessage = async () => {
    if (!question.trim()) return;

    const userMessage = {
      role: "user",
      text: question,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);
    scrollToBottom();

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/chat",
        { question }
      );

      const botMessage = {
        role: "assistant",
        text: response.data.answer,
        sources: response.data.sources,
        route: response.data.route,
        timings: response.data.timings,
      };

      // Log detailed timings to console
      console.log("⏱️ LATENCY BREAKDOWN:");
      if (response.data.timings) {
        const timings = response.data.timings;
        const total = timings.total || 0;
        Object.entries(timings).forEach(([key, value]) => {
          if (key !== "total") {
            const percentage = ((value / total) * 100).toFixed(1);
            console.log(`   ${key}: ${value.toFixed(3)}s (${percentage}%)`);
          }
        });
        console.log(`   TOTAL: ${total.toFixed(3)}s (100%)`);
      }

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: {
            summary: "❌ Error connecting to backend",
            details: "Please check if the API is running",
            key_points: [],
          },
        },
      ]);
    }

    setLoading(false);
    scrollToBottom();
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !loading) {
      sendMessage();
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0a0e27 0%, #16213e 25%, #0f1629 50%, #1a1f3a 75%, #0d1a2d 100%)",
        padding: "0",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        overflow: "hidden",
      }}
    >
      {/* Animated Background Elements */}
      <div
        style={{
          position: "fixed",
          top: "0",
          left: "0",
          width: "100%",
          height: "100%",
          pointerEvents: "none",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "-50%",
            left: "-50%",
            width: "200%",
            height: "200%",
            background: "radial-gradient(circle, rgba(96, 165, 250, 0.1) 0%, transparent 50%)",
            animation: "float 20s ease-in-out infinite",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: "-50%",
            right: "-50%",
            width: "200%",
            height: "200%",
            background: "radial-gradient(circle, rgba(167, 139, 250, 0.1) 0%, transparent 50%)",
            animation: "float 25s ease-in-out infinite 5s",
          }}
        />
      </div>

      {/* Main Container */}
      <div
        style={{
          position: "relative",
          zIndex: "10",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          maxHeight: "100vh",
        }}
      >
        {/* Header */}
        <div
          style={{
            textAlign: "center",
            padding: "20px 16px",
            background: "linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.3) 100%)",
            borderBottom: "1px solid rgba(100, 165, 250, 0.2)",
            backdropFilter: "blur(10px)",
            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.3)",
          }}
        >
          <div style={{ 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center", 
            gap: "12px", 
            marginBottom: "8px",
            flexWrap: "wrap",
          }}>
            <span style={{ fontSize: "clamp(28px, 8vw, 40px)", animation: "bounce 2s ease-in-out infinite", flexShrink: 0 }}>🤖</span>
            <h1
              style={{
                fontSize: "clamp(28px, 7vw, 48px)",
                fontWeight: "900",
                margin: "0",
                background: "linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #3b82f6 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
                letterSpacing: "-1px",
                wordBreak: "break-word",
                lineHeight: "1.1",
              }}
            >
              Agentic RAG
            </h1>
            <span style={{ fontSize: "clamp(28px, 8vw, 40px)", animation: "pulse-glow 2s ease-in-out infinite", flexShrink: 0 }}>✨</span>
          </div>
          <p style={{ 
            color: "#cbd5e1", 
            fontSize: "clamp(11px, 3vw, 13px)", 
            letterSpacing: "2px", 
            marginTop: "5px", 
            fontWeight: "600", 
            textTransform: "uppercase",
            margin: "5px auto 0",
          }}>
            Intelligent Document Retrieval System
          </p>
        </div>

        {/* Chat Container */}
        <div
          style={{
            flex: "1",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            padding: "clamp(12px, 3vw, 20px)",
            maxWidth: "1200px",
            width: "100%",
            margin: "0 auto",
          }}
        >
          {/* Messages Area */}
          <div
            data-messages-container
            style={{
              flex: "1",
              overflowY: "auto",
              background: "rgba(15, 23, 42, 0.4)",
              border: "1px solid rgba(100, 165, 250, 0.15)",
              borderRadius: "24px",
              padding: "clamp(16px, 3vw, 24px)",
              marginBottom: "20px",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.02)",
              backdropFilter: "blur(20px)",
              display: "flex",
              flexDirection: "column",
              gap: "16px",
              scrollBehavior: "smooth",
            }}
          >
            {messages.length === 0 ? (
              <div style={{ 
                display: "flex", 
                flexDirection: "column", 
                alignItems: "center", 
                justifyContent: "center", 
                height: "100%", 
                color: "#64748b", 
                textAlign: "center",
                padding: "clamp(12px, 3vw, 20px)",
              }}>
                <div style={{ fontSize: "clamp(80px, 20vw, 120px)", marginBottom: "20px", opacity: 0.2, animation: "float 3s ease-in-out infinite" }}>
                  🔍
                </div>
                <h2 style={{ fontSize: "clamp(22px, 5vw, 28px)", fontWeight: "700", marginBottom: "12px", background: "linear-gradient(135deg, #60a5fa, #a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                  Welcome to Agentic RAG
                </h2>
                <p style={{ fontSize: "clamp(13px, 3vw, 15px)", maxWidth: "350px", color: "#94a3b8", lineHeight: "1.6" }}>
                  Ask questions about your documents and get intelligent, AI-powered answers backed by real content.
                </p>
                <div style={{ marginTop: "30px", display: "flex", gap: "10px", flexWrap: "wrap", justifyContent: "center" }}>
                  {["2+2", "What is AI?", "Define machine learning"].map((hint, i) => (
                    <button
                      key={i}
                      onClick={() => setQuestion(hint)}
                      style={{
                        padding: "clamp(7px, 2vw, 8px) clamp(12px, 3vw, 16px)",
                        background: "rgba(96, 165, 250, 0.1)",
                        border: "1px solid rgba(96, 165, 250, 0.3)",
                        borderRadius: "20px",
                        color: "#60a5fa",
                        fontSize: "clamp(11px, 2vw, 12px)",
                        cursor: "pointer",
                        transition: "all 0.3s ease",
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = "rgba(96, 165, 250, 0.2)";
                        e.target.style.transform = "translateY(-2px)";
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = "rgba(96, 165, 250, 0.1)";
                        e.target.style.transform = "translateY(0)";
                      }}
                    >
                      {hint}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  <Message role={msg.role} text={msg.text} timings={msg.timings} />

                  {msg.sources && msg.sources.length > 0 && (
                    <div
                      style={{
                        fontSize: "11px",
                        color: "#64b5f6",
                        marginTop: "4px",
                        marginLeft: msg.role === "user" ? "auto" : "0",
                        maxWidth: "70%",
                        textAlign: msg.role === "user" ? "right" : "left",
                        background: "rgba(100, 165, 250, 0.05)",
                        padding: "8px 12px",
                        borderRadius: "12px",
                        border: "1px solid rgba(100, 165, 250, 0.2)",
                      }}
                    >
                      <div style={{ fontWeight: "700", marginBottom: "4px", display: "flex", alignItems: "center", gap: "4px" }}>
                        <span>📚</span>
                        <span>SOURCES</span>
                      </div>
                      {msg.sources.map((source, i) => (
                        <div key={i} style={{ paddingLeft: "20px", marginBottom: "2px" }}>
                          → {source.split("/").pop()}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}

            {loading && (
              <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "16px" }}>
                <div style={{ display: "flex", gap: "4px" }}>
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      style={{
                        width: "8px",
                        height: "8px",
                        borderRadius: "50%",
                        background: "#64b5f6",
                        animation: `bounce-dots 1.4s ease-in-out ${i * 0.2}s infinite`,
                      }}
                    />
                  ))}
                </div>
                <span style={{ fontSize: "14px", fontWeight: "500", color: "#64b5f6" }}>AI is thinking...</span>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div
            style={{
              display: "flex",
              gap: "clamp(8px, 2vw, 12px)",
              background: "rgba(30, 41, 59, 0.6)",
              border: "1px solid rgba(100, 165, 250, 0.2)",
              borderRadius: "20px",
              padding: "clamp(10px, 2vw, 14px)",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05)",
              backdropFilter: "blur(20px)",
              transition: "all 0.3s ease",
              flexWrap: "wrap",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "rgba(100, 165, 250, 0.5)";
              e.currentTarget.style.boxShadow = "0 8px 32px rgba(96, 165, 250, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "rgba(100, 165, 250, 0.2)";
              e.currentTarget.style.boxShadow = "0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05)";
            }}
          >
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              disabled={loading}
              style={{
                flex: "1",
                minWidth: "150px",
                padding: "clamp(10px, 2vw, 12px) clamp(12px, 3vw, 16px)",
                border: "none",
                borderRadius: "14px",
                background: "rgba(15, 23, 42, 0.8)",
                color: "#e2e8f0",
                fontSize: "clamp(13px, 2vw, 14px)",
                outline: "none",
                transition: "all 0.3s ease",
                boxShadow: "inset 0 1px 3px rgba(0, 0, 0, 0.2)",
              }}
              onFocus={(e) => {
                e.target.style.boxShadow = "inset 0 0 8px rgba(100, 165, 250, 0.3)";
                e.target.style.background = "rgba(15, 23, 42, 0.95)";
              }}
              onBlur={(e) => {
                e.target.style.boxShadow = "inset 0 1px 3px rgba(0, 0, 0, 0.2)";
                e.target.style.background = "rgba(15, 23, 42, 0.8)";
              }}
            />

            <button
              onClick={sendMessage}
              disabled={loading}
              style={{
                padding: "clamp(10px, 2vw, 12px) clamp(18px, 4vw, 24px)",
                borderRadius: "14px",
                border: "none",
                background: loading
                  ? "linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)"
                  : "linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%)",
                color: "white",
                fontWeight: "700",
                fontSize: "clamp(12px, 2vw, 14px)",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "all 0.3s ease",
                boxShadow: "0 4px 15px rgba(96, 165, 250, 0.4)",
                opacity: loading ? 0.7 : 1,
                transform: "translateY(0)",
                whiteSpace: "nowrap",
                flexShrink: 0,
              }}
              onMouseEnter={(e) => {
                if (!loading) {
                  e.target.style.transform = "translateY(-2px)";
                  e.target.style.boxShadow = "0 8px 25px rgba(96, 165, 250, 0.6)";
                }
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = "translateY(0)";
                e.target.style.boxShadow = "0 4px 15px rgba(96, 165, 250, 0.4)";
              }}
            >
              {loading ? "⏳" : "Send ⚡"}
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(30px);
          }
        }

        @keyframes pulse-glow {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.8;
            transform: scale(1.1);
          }
        }

        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        @keyframes bounce-dots {
          0%, 80%, 100% {
            transform: translateY(0);
            opacity: 1;
          }
          40% {
            transform: translateY(-10px);
            opacity: 0.7;
          }
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        [data-messages-container]::-webkit-scrollbar {
          width: 6px;
        }

        [data-messages-container]::-webkit-scrollbar-track {
          background: transparent;
        }

        [data-messages-container]::-webkit-scrollbar-thumb {
          background: rgba(100, 165, 250, 0.3);
          border-radius: 10px;
        }

        [data-messages-container]::-webkit-scrollbar-thumb:hover {
          background: rgba(100, 165, 250, 0.5);
        }
      `}</style>
    </div>
  );
}

export default ChatBox;