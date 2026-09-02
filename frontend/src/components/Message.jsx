import { useState } from "react";
import "./Message.css";

function Message({ role, text, timings }) {
  const isAssistant = role === 'assistant';
  const isStructured = typeof text === 'object' && text !== null;
  const [showTimings, setShowTimings] = useState(false);

  return (
    <div
      className={`message-wrapper ${isAssistant ? 'assistant' : 'user'}`}
    >
      <div className={`message-content ${isAssistant ? 'assistant' : 'user'}`}>
        {isStructured ? (
          <div className="structured-message">
            {text.summary && (
              <div className="message-summary">
                <span className="summary-icon">📌</span>
                <span>{text.summary}</span>
              </div>
            )}

            {text.details && (
              <div className="message-details">
                {text.details}
              </div>
            )}

            {text.key_points && text.key_points.length > 0 && (
              <div className="key-points-section">
                <div className="key-points-header">
                  <span>⚡</span>
                  <span>Key Insights</span>
                </div>
                <ul className="key-points-list">
                  {text.key_points.map((point, idx) => (
                    <li key={idx} className="key-point-item">
                      <span className="point-bullet">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {text.sources && text.sources.length > 0 && (
              <div className="sources-section">
                <div className="sources-header">
                  <span>📎</span>
                  <span>Sources</span>
                </div>
                <div className="sources-list">
                  {text.sources.map((source, idx) => (
                    <div key={idx} className="source-item">
                      <span className="source-icon">📄</span>
                      <span className="source-text">{source}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="simple-message">
            {text}
          </div>
        )}

        {timings && Object.keys(timings).length > 0 && (
          <div className="timings-section">
            <button
              className="timings-toggle"
              onClick={() => setShowTimings(!showTimings)}
              title="Toggle timing details"
            >
              <span className="timing-icon">⏱</span>
              <span className="timing-label">
                {showTimings ? 'Hide' : 'Show'} Performance
              </span>
            </button>
            {showTimings && (
              <div className="timings-details">
                {Object.entries(timings).map(([key, value]) => (
                  <div key={key} className="timing-item">
                    <span className="timing-key">
                      {key.replace(/_/g, ' ')}:
                    </span>
                    <span className="timing-value">
                      {typeof value === "number" ? `${value.toFixed(2)}s` : value}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;
