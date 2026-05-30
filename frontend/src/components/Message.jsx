import React, { useState } from 'react';

function Message({ role, text, timings }) {
  const isAssistant = role === "assistant";
  const isStructured = typeof text === "object" && text !== null;
  const [showTimings, setShowTimings] = useState(false);

  return (
    <div
      style={{
        display: "flex",
        justifyContent: role === "user" ? "flex-end" : "flex-start",
        marginBottom: "12px",
        animation: "slideIn 0.4s ease",
      }}
    >
      <div
        style={{
          maxWidth: "clamp(70%, 90vw, 75%)",
          padding: isStructured ? "clamp(14px, 3vw, 18px)" : "clamp(12px, 2vw, 14px) clamp(12px, 3vw, 18px)",
          borderRadius: "18px",
          background: isAssistant
            ? "linear-gradient(135deg, rgba(30, 58, 138, 0.5) 0%, rgba(59, 130, 246, 0.25) 100%)"
            : "linear-gradient(135deg, #3b82f6 0%, #1e40af 100%)",
          border: isAssistant
            ? "1px solid rgba(96, 165, 250, 0.35)"
            : "1px solid rgba(59, 130, 246, 0.6)",
          color: "#e2e8f0",
          lineHeight: "1.7",
          fontSize: "clamp(13px, 2vw, 14px)",
          boxShadow: isAssistant
            ? "0 4px 20px rgba(96, 165, 250, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05)"
            : "0 4px 20px rgba(59, 130, 246, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(15px)",
          position: "relative",
        }}
      >
        {isStructured ? (
          <div style={{ color: "#e2e8f0" }}>
            {text.summary && (
              <div
                style={{
                  fontWeight: "800",
                  marginBottom: "12px",
                  fontSize: "clamp(14px, 2vw, 15px)",
                  color: "#60a5fa",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  letterSpacing: "0.3px",
                }}
              >
                <span style={{ fontSize: "clamp(14px, 3vw, 16px)" }}>📌</span>
                <span>{text.summary}</span>
              </div>
            )}

            {text.details && (
              <div
                style={{
                  marginBottom: "14px",
                  fontSize: "clamp(12px, 2vw, 14px)",
                  color: "#cbd5e1",
                  lineHeight: "1.8",
                  fontWeight: "400",
                }}
              >
                {text.details}
              </div>
            )}

            {text.key_points && text.key_points.length > 0 && (
              <div style={{ marginTop: "14px", paddingTop: "12px", borderTop: "1px solid rgba(96, 165, 250, 0.25)" }}>
                <div
                  style={{
                    fontWeight: "800",
                    marginBottom: "10px",
                    fontSize: "clamp(11px, 2vw, 12px)",
                    color: "#a78bfa",
                    textTransform: "uppercase",
                    letterSpacing: "0.8px",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <span>⚡</span>
                  <span>Key Insights</span>
                </div>
                <ul
                  style={{
                    marginTop: "8px",
                    paddingLeft: "0",
                    listStyle: "none",
                  }}
                >
                  {text.key_points.map((point, idx) => (
                    <li
                      key={idx}
                      style={{
                        marginBottom: "8px",
                        color: "#cbd5e1",
                        fontSize: "clamp(12px, 2vw, 13px)",
                        position: "relative",
                        paddingLeft: "24px",
                        background: "rgba(167, 139, 250, 0.05)",
                        padding: "8px 12px 8px 24px",
                        borderRadius: "10px",
                        border: "1px solid rgba(167, 139, 250, 0.15)",
                        fontWeight: "500",
                      }}
                    >
                      <span
                        style={{
                          position: "absolute",
                          left: "10px",
                          color: "#a78bfa",
                          fontWeight: "bold",
                          fontSize: "14px",
                        }}
                      >
                        ▸
                      </span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {timings && isAssistant && (
              <div style={{ marginTop: "12px", paddingTop: "12px", borderTop: "1px solid rgba(96, 165, 250, 0.25)" }}>
                <button
                  onClick={() => setShowTimings(!showTimings)}
                  style={{
                    background: "rgba(96, 165, 250, 0.15)",
                    border: "1px solid rgba(96, 165, 250, 0.3)",
                    color: "#60a5fa",
                    padding: "6px 12px",
                    borderRadius: "8px",
                    cursor: "pointer",
                    fontSize: "11px",
                    fontWeight: "600",
                    transition: "all 0.3s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = "rgba(96, 165, 250, 0.25)";
                    e.target.style.borderColor = "rgba(96, 165, 250, 0.5)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = "rgba(96, 165, 250, 0.15)";
                    e.target.style.borderColor = "rgba(96, 165, 250, 0.3)";
                  }}
                >
                  ⏱️ {showTimings ? "Hide" : "Show"} Latency ({timings.total?.toFixed(2)}s)
                </button>

                {showTimings && (
                  <div
                    style={{
                      marginTop: "10px",
                      background: "rgba(96, 165, 250, 0.08)",
                      padding: "10px",
                      borderRadius: "10px",
                      border: "1px solid rgba(96, 165, 250, 0.2)",
                      fontSize: "11px",
                      fontFamily: "monospace",
                      color: "#cbd5e1",
                    }}
                  >
                    {Object.entries(timings).map(([key, value]) => {
                      if (key === "total") return null;
                      const percentage = timings.total ? ((value / timings.total) * 100).toFixed(1) : 0;
                      return (
                        <div key={key} style={{ marginBottom: "4px", display: "flex", justifyContent: "space-between" }}>
                          <span>{key}:</span>
                          <span style={{ color: "#60a5fa" }}>
                            {value.toFixed(3)}s ({percentage}%)
                          </span>
                        </div>
                      );
                    })}
                    <div
                      style={{
                        marginTop: "6px",
                        paddingTop: "6px",
                        borderTop: "1px solid rgba(96, 165, 250, 0.2)",
                        fontWeight: "600",
                        display: "flex",
                        justifyContent: "space-between",
                        color: "#a78bfa",
                      }}
                    >
                      <span>TOTAL:</span>
                      <span>{timings.total?.toFixed(3)}s</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <span style={{ fontWeight: "500" }}>{text}</span>
        )}
      </div>

      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(12px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
    </div>
  );
}

export default Message;