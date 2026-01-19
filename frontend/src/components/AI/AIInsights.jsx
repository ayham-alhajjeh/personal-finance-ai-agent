import { useState } from 'react';
import './AIInsights.css';

function AIInsights({ insights }) {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateInsights = () => {
    setIsGenerating(true);
    // Simulate AI generation
    setTimeout(() => {
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <div className="ai-insights-card">
      <div className="insights-header">
        <div className="header-left">
          <h3>🤖 AI Insights</h3>
          <p className="card-subtitle">Personalized financial recommendations</p>
        </div>
        <div className="header-right">
          <button
            className="btn-secondary"
            onClick={handleGenerateInsights}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <span className="spinner-small"></span>
                Generating...
              </>
            ) : (
              <>✨ Generate New Insights</>
            )}
          </button>
        </div>
      </div>

      <div className="insights-content">
        {insights && insights.length > 0 ? (
          <ul className="insights-list">
            {insights.map((insight, index) => (
              <li key={index} className="insight-item">
                <span className="insight-bullet">•</span>
                <span className="insight-text">{insight}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="empty-insights">
            <span className="empty-icon">💡</span>
            <p>No insights generated yet</p>
            <p className="empty-subtitle">Click "Generate Insights" to get started</p>
          </div>
        )}
      </div>

      <div className="insights-footer">
        <button className="btn-link">View Insight History →</button>
      </div>
    </div>
  );
}

export default AIInsights;
