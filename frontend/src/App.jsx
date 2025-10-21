import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [postUrl, setPostUrl] = useState('');
  const [comments, setComments] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [latestPost, setLatestPost] = useState('');
  const [apiConnected, setApiConnected] = useState(false);
  const [checkingConnection, setCheckingConnection] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!postUrl.trim()) return;

    setLoading(true);
    setError('');
    setComments(null);

    try {
      // Store the post URL
      const response = await fetch(`${API_BASE_URL}/posturl`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: postUrl }),
      });

      if (!response.ok) {
        throw new Error('Failed to store post URL');
      }

      const result = await response.json();
      setLatestPost(result.stored_url);

      // Fetch comments
      const commentsResponse = await fetch(`${API_BASE_URL}/latestpost/comments`);
      if (!commentsResponse.ok) {
        throw new Error('Failed to fetch comments');
      }

      const commentsData = await commentsResponse.json();
      // Handle the nested structure from the API
      if (commentsData.success && commentsData.comments) {
        setComments(commentsData.comments);
      } else if (commentsData.error) {
        throw new Error(commentsData.error);
      } else {
        setComments(commentsData);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const checkApiConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });
      setApiConnected(response.ok);
    } catch (err) {
      setApiConnected(false);
    } finally {
      setCheckingConnection(false);
    }
  };

  const getLatestPost = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/latestpost`);
      if (response.ok) {
        const data = await response.json();
        setLatestPost(data.latest_post || '');
      }
    } catch (err) {
      console.error('Failed to fetch latest post:', err);
    }
  };

  useEffect(() => {
    // Initial API connection check
    checkApiConnection();
    getLatestPost();

    // Set up periodic connection checks every 30 seconds
    const connectionInterval = setInterval(() => {
      if (!apiConnected) {
        checkApiConnection();
      }
    }, 30000);

    return () => clearInterval(connectionInterval);
  }, [apiConnected]);

  const getSentimentColor = (label) => {
    switch (label) {
      case 'POSITIVE':
        return '#4ade80';
      case 'NEGATIVE':
        return '#f87171';
      case 'NEUTRAL':
        return '#94a3b8';
      default:
        return '#6b7280';
    }
  };

  const getSentimentEmoji = (label) => {
    switch (label) {
      case 'POSITIVE':
        return '😊';
      case 'NEGATIVE':
        return '😞';
      case 'NEUTRAL':
        return '😐';
      default:
        return '🤔';
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-text">
            <h1>🔍 Reddit Sentiment Analysis</h1>
            <p>Analyze the sentiment of Reddit post comments</p>
          </div>
          <div className="connection-status">
            {checkingConnection ? (
              <div className="status-indicator checking">
                <div className="status-dot checking"></div>
                <span>Checking connection...</span>
              </div>
            ) : apiConnected ? (
              <div className="status-indicator connected">
                <div className="status-dot connected"></div>
                <span>API Connected</span>
              </div>
            ) : (
              <div className="status-indicator disconnected">
                <div className="status-dot disconnected"></div>
                <span>API Disconnected</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="input-section">
          <form onSubmit={handleSubmit} className="url-form">
            <div className="input-group">
              <input
                type="url"
                value={postUrl}
                onChange={(e) => setPostUrl(e.target.value)}
                placeholder="Enter Reddit post URL..."
                className="url-input"
                disabled={loading}
              />
              <button 
                type="submit" 
                className="analyze-btn"
                disabled={loading || !postUrl.trim()}
              >
                {loading ? 'Analyzing...' : 'Analyze Comments'}
              </button>
            </div>
          </form>

          {latestPost && (
            <div className="latest-post">
              <h3>📌 Latest Post:</h3>
              <a href={latestPost} target="_blank" rel="noopener noreferrer" className="post-link">
                {latestPost}
              </a>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Fetching and analyzing comments...</p>
          </div>
        )}

        {comments && (
          <div className="results-section">
            <h2>📊 Analysis Results</h2>
            <div className="stats">
              <div className="stat-item">
                <span className="stat-number">{Object.keys(comments).length}</span>
                <span className="stat-label">Total Comments</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">
                  {Object.values(comments).filter(c => c.label === 'POSITIVE').length}
                </span>
                <span className="stat-label">Positive</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">
                  {Object.values(comments).filter(c => c.label === 'NEGATIVE').length}
                </span>
                <span className="stat-label">Negative</span>
              </div>
            </div>

            <div className="comments-list">
              {Object.entries(comments).map(([id, comment]) => (
                <div key={id} className="comment-card">
                  <div className="comment-header">
                    <span className="comment-id">#{id}</span>
                    <div 
                      className="sentiment-badge"
                      style={{ backgroundColor: getSentimentColor(comment.label) }}
                    >
                      {getSentimentEmoji(comment.label)} {comment.label === 'POSITIVE' ? 'Positive' : comment.label === 'NEGATIVE' ? 'Negative' : comment.label}
                    </div>
                    <span className="confidence-score">
                      {(comment.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="comment-content">
                    <p className="comment-text">{comment.comment}</p>
                    <div className="comment-metadata">
                      <span className="metadata-item">
                        <strong>Sentiment:</strong> {comment.label === 'POSITIVE' ? 'Positive' : comment.label === 'NEGATIVE' ? 'Negative' : comment.label}
                      </span>
                      <span className="metadata-item">
                        <strong>Confidence:</strong> {(comment.score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI & Transformers</p>
      </footer>
    </div>
  );
}

export default App;