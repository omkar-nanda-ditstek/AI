import React, { useState, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileChange = (selectedFile) => {
    setFile(selectedFile);
    setResult(null);
    setError(null);
    setUploadProgress(0);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload-resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });

      if (response.data.success) {
        setResult(response.data);
        setUploadProgress(100);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>🤖 Resume Parser AI</h1>
          <p>Upload your resume and get instant AI-powered analysis</p>
        </div>
      </header>

      <div className="main-content">
        <div className={`upload-section ${dragActive ? 'drag-active' : ''}`}
             onDragEnter={handleDrag}
             onDragLeave={handleDrag}
             onDragOver={handleDrag}
             onDrop={handleDrop}>
          
          {!file ? (
            <div className="upload-placeholder">
              <div className="upload-icon">📄</div>
              <h3>Drop your resume here or click to browse</h3>
              <p>Supports PDF, DOCX, and TXT files</p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => handleFileChange(e.target.files[0])}
                className="file-input-hidden"
              />
              <button 
                type="button" 
                className="browse-btn"
                onClick={() => fileInputRef.current?.click()}
              >
                Browse Files
              </button>
            </div>
          ) : (
            <div className="file-selected">
              <div className="file-info">
                <div className="file-icon">📄</div>
                <div className="file-details">
                  <h4>{file.name}</h4>
                  <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button 
                  type="button" 
                  className="remove-file"
                  onClick={resetForm}
                >
                  ✕
                </button>
              </div>
              
              {loading && (
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <p className="progress-text">{uploadProgress}% uploaded</p>
                </div>
              )}
              
              <button 
                type="button" 
                className="upload-btn"
                onClick={handleUpload}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Processing...
                  </>
                ) : (
                  <>
                    🚀 Parse Resume
                  </>
                )}
              </button>
            </div>
          )}
        </div>

      {error && (
        <div className="error-banner animate-in">
          <div className="error-icon">⚠️</div>
          <div>
            <h3>Upload Failed</h3>
            <p>{error}</p>
          </div>
          <button className="retry-btn" onClick={resetForm}>
            Try Again
          </button>
        </div>
      )}

        {result && (
          <div className="results animate-in">
            <div className="success-banner">
              <div className="success-icon">🎉</div>
              <div>
                <h3>Resume Parsed Successfully!</h3>
                <p>Your resume has been analyzed and saved to the database</p>
              </div>
              <button className="new-upload-btn" onClick={resetForm}>
                Upload Another
              </button>
            </div>

            <div className="results-grid">
              <div className="card parsed-data">
                <div className="card-header">
                  <h3>👤 Personal Information</h3>
                </div>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">Name:</span>
                    <span className="value">{result.data.parsed_resume.name || 'Not found'}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Email:</span>
                    <span className="value">{result.data.parsed_resume.email || 'Not found'}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Phone:</span>
                    <span className="value">{result.data.parsed_resume.phone || 'Not found'}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Experience:</span>
                    <span className="value">{result.data.parsed_resume.experience || 'Not specified'}</span>
                  </div>
                </div>
              </div>

              <div className="card skills-section">
                <div className="card-header">
                  <h3>🛠️ Skills</h3>
                </div>
                <div className="skills-container">
                  {result.data.parsed_resume.skills?.length > 0 ? (
                    result.data.parsed_resume.skills.map((skill, index) => (
                      <span key={index} className="skill-tag">{skill}</span>
                    ))
                  ) : (
                    <p className="no-data">No skills detected</p>
                  )}
                </div>
              </div>

              <div className="card projects-section">
                <div className="card-header">
                  <h3>🚀 Projects</h3>
                </div>
                <div className="projects-container">
                  {result.data.parsed_resume.projects?.length > 0 ? (
                    result.data.parsed_resume.projects.map((project, index) => (
                      <div key={index} className="project-item">{project}</div>
                    ))
                  ) : (
                    <p className="no-data">No projects detected</p>
                  )}
                </div>
              </div>

              <div className="card questions-section">
                <div className="card-header">
                  <h3>❓ Interview Questions</h3>
                </div>
                <div className="questions-container">
                  {result.data.questions?.map((q, index) => (
                    <div key={q.id} className="question-card">
                      <div className="question-number">Q{index + 1}</div>
                      <div className="question-text">{q.question}</div>
                      <div className="question-type">{q.type}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="session-info">
              <div className="session-details">
                <p><strong>Session ID:</strong> <code>{result.data.session_id}</code></p>
                <p><strong>Resume ID:</strong> <code>{result.data.resume_id}</code></p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;