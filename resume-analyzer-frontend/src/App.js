import React from 'react';
import { useState } from 'react';
import './App.css'

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid PDF file');
      setFile(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('Please drop a valid PDF file');
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze resume');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message || 'Error analyzing resume');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResults(null);
    setError(null);
  };

  return (
    <div className="App">
      <header className="header">
        <h1>📄 Resume Analyzer</h1>
        <p>Get instant AI feedback on your resume</p>
      </header>

      <main className="container">
        {!results ? (
          <div className="upload-section">
            <div
              className="upload-box"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <div className="upload-icon">📤</div>
              <div className="upload-text">Drag your resume here</div>
              <div className="upload-subtext">or click to select PDF</div>
              <input
                type="file"
                id="fileInput"
                accept=".pdf"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <label htmlFor="fileInput" className="file-input-label">
                Click to select
              </label>
              {file && <div className="file-name">✓ {file.name}</div>}
            </div>

            {error && <div className="error">{error}</div>}

            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className="analyze-btn"
            >
              {loading ? 'Analyzing...' : 'Analyze Resume'}
            </button>
          </div>
        ) : (
          <div className="results-section">
            <div className="score-card">
              <div className="score-number">{results.overall_score}</div>
              <div className="score-label">Overall Score</div>
            </div>

            <div className="result-group">
              <h2>💪 Strengths</h2>
              <ul className="result-list">
                {results.strengths.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="result-group">
              <h2>⚡ Areas for Improvement</h2>
              <ul className="result-list">
                {results.improvements.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="result-group">
              <h2>📋 Missing Sections</h2>
              <ul className="result-list">
                {results.missing_sections.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="result-group">
              <h2>✨ Action Items</h2>
              <ul className="result-list">
                {results.action_items.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>

            <button onClick={handleReset} className="reset-btn">
              Analyze Another Resume
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;