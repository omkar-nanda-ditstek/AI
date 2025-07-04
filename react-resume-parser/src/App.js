import React, { useState, useRef } from "react";
import axios from "axios";
import Interview from "./Interview";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [showSkillsModal, setShowSkillsModal] = useState(false);
  const [userSkills, setUserSkills] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [availableSkills] = useState([
    "JavaScript",
    "Python",
    "Java",
    "C++",
    "React",
    "Node.js",
    "Angular",
    "Vue.js",
    "HTML",
    "CSS",
    "MongoDB",
    "MySQL",
    "PostgreSQL",
    "AWS",
    "Docker",
    "Kubernetes",
    "Git",
    "Linux",
    "TypeScript",
    "PHP",
    "Ruby",
    "Go",
    "Swift",
    "Kotlin",
    "Django",
    "Flask",
    "Express.js",
    "Spring Boot",
    "Laravel",
    "Rails",
    "Redux",
    "GraphQL",
    "REST API",
    "Microservices",
    "DevOps",
    "CI/CD",
  ]);
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
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
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
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://localhost:8000/upload-resume",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setUploadProgress(progress);
          },
        }
      );

      if (response.data.success) {
        setResult(response.data);
        setUploadProgress(100);
        console.log("Resume uploaded with ID:", response.data.data.resume_id);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setUploadProgress(0);
    setInterviewStarted(false);
    setCurrentQuestion(0);
    setAnswers([]);
    setCurrentAnswer("");
    setShowSkillsModal(false);
    setUserSkills([]);
    setIsSubmitting(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const openSkillsModal = () => {
    setUserSkills([...result.data.parsed_resume.skills] || []);
    setShowSkillsModal(true);
  };

  const closeSkillsModal = () => {
    setShowSkillsModal(false);
  };

  const toggleSkill = (skill) => {
    // Update UI immediately for better UX
    setUserSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  const removeSkill = async (skill) => {
    try {
      const response = await axios.delete(
        `http://localhost:8000/remove-skill/${result.data.resume_id}`,
        {
          data: { skill: skill },
        }
      );

      if (response.data.success) {
        // Update main result state
        setResult((prev) => ({
          ...prev,
          data: {
            ...prev.data,
            parsed_resume: {
              ...prev.data.parsed_resume,
              skills: prev.data.parsed_resume.skills.filter((s) => s !== skill),
            },
          },
        }));
        alert(`Skill '${skill}' removed successfully!`);
      } else {
        alert(`Error: ${response.data.message}`);
      }
    } catch (err) {
      console.error("Error removing skill:", err);
      alert(
        `Error removing skill: ${err.response?.data?.message || err.message}`
      );
    }
  };



  const saveSkills = async () => {
    try {
      const response = await axios.put(
        `http://localhost:8000/update-skills/${result.data.resume_id}`,
        {
          skills: userSkills,
        }
      );

      if (response.data.success) {
        setResult((prev) => ({
          ...prev,
          data: {
            ...prev.data,
            parsed_resume: {
              ...prev.data.parsed_resume,
              skills: userSkills,
            },
          },
        }));
        setShowSkillsModal(false);
        alert("Skills updated successfully!");
      } else {
        alert(`Error: ${response.data.message}`);
      }
    } catch (err) {
      console.error("Error updating skills:", err);
      alert(
        `Error updating skills: ${err.response?.data?.message || err.message}`
      );
    }
  };

  const startInterview = () => {
    setInterviewStarted(true);
    setCurrentQuestion(0);
    setAnswers([]);
    setCurrentAnswer("");
  };



  const nextQuestion = () => {
    const newAnswers = [
      ...answers,
      {
        question_id: result.data.questions[currentQuestion].id,
        answer: currentAnswer,
      },
    ];
    setAnswers(newAnswers);
    setCurrentAnswer("");

    if (currentQuestion < result.data.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Interview completed
      submitInterview(newAnswers);
    }
  };

  const submitInterview = async (finalAnswers) => {
    if (isSubmitting) {
      console.log('Already submitting, ignoring duplicate call');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      console.log('=== SUBMITTING INTERVIEW ===');
      
      const requestData = {
        session_id: result.data.session_id,
        resume_id: result.data.resume_id,
        responses: finalAnswers,
      };
      
      console.log('Request data:', requestData);
      
      const response = await axios.post(
        "http://localhost:8000/submit-interview",
        requestData,
        {
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      console.log('=== RESPONSE RECEIVED ===');
      console.log('Status:', response.status);
      console.log('Response data:', response.data);
      
      if (response.status === 200 && response.data) {
        if (response.data.success) {
          alert('Interview completed successfully!');
        } else {
          alert(`Error: ${response.data.message || 'Unknown error'}`);
        }
      } else {
        alert('Invalid response from server');
      }
      
    } catch (err) {
      console.error('=== ERROR SUBMITTING INTERVIEW ===');
      console.error('Error:', err);
      
      if (err.code === 'ECONNABORTED') {
        alert('Request timeout - please try again');
      } else if (err.response) {
        console.error('Error status:', err.response.status);
        console.error('Error data:', err.response.data);
        alert(`Server error (${err.response.status}): ${err.response.data?.message || 'Unknown error'}`);
      } else {
        alert(`Network error: ${err.message}`);
      }
    } finally {
      setIsSubmitting(false);
      endInterview();
    }
  };

  const endInterview = () => {
    setInterviewStarted(false);
  };

  return (
    <div className={`App ${interviewStarted ? 'interview-mode' : ''}`}>
      {!interviewStarted && (
        <header className="App-header">
          <div className="header-content">
            <h1>🤖 Resume Parser AI</h1>
            <p>Upload your resume and get instant AI-powered analysis</p>
          </div>
        </header>
      )}

      <div className="main-content">
        <div
          className={`upload-section ${dragActive ? "drag-active" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
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
                  <>🚀 Parse Resume</>
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
                    <span className="value">
                      {result.data.parsed_resume.name || "Not found"}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="label">Email:</span>
                    <span className="value">
                      {result.data.parsed_resume.email || "Not found"}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="label">Phone:</span>
                    <span className="value">
                      {result.data.parsed_resume.phone || "Not found"}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="label">Experience:</span>
                    <span className="value">
                      {result.data.parsed_resume.experience || "Not specified"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="card skills-section">
                <div className="card-header">
                  <h3>🛠️ Skills</h3>
                  <button className="edit-skills-btn" onClick={openSkillsModal}>
                    ✏️ Edit Skills
                  </button>
                </div>
                <div className="skills-container">
                  {result.data.parsed_resume.skills?.length > 0 ? (
                    result.data.parsed_resume.skills.map((skill, index) => (
                      <span key={index} className="skill-tag removable">
                        {skill}
                        <button
                          className="remove-skill-btn"
                          onClick={() => removeSkill(skill)}
                          title="Remove skill"
                        >
                          ✕
                        </button>
                      </span>
                    ))
                  ) : (
                    <p className="no-data">No skills detected</p>
                  )}
                </div>
              </div>

              {!interviewStarted ? (
                <div className="card interview-section">
                  <div className="card-header">
                    <h3>🎯 Interview Ready</h3>
                  </div>
                  <div className="interview-info">
                    <button
                      className="start-interview-btn"
                      onClick={startInterview}
                    >
                      🚀 Start Interview
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}

        {/* Interview Component */}
        {interviewStarted && (
          <div className="interview-fullscreen">
            <Interview 
              questions={result.data.questions}
              sessionId={result.data.session_id}
              resumeId={result.data.resume_id}
              onComplete={submitInterview}
            />
          </div>
        )}

        {/* Skills Modal */}
        {showSkillsModal && (
          <div className="modal-overlay" onClick={closeSkillsModal}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>🛠️ Manage Skills</h3>
                <button className="modal-close" onClick={closeSkillsModal}>
                  ✕
                </button>
              </div>
              <div className="modal-body">
                <div className="skills-section">
                  <h4>📋 Current Skills</h4>
                  <div className="current-skills">
                    {userSkills.length > 0 ? (
                      userSkills.map((skill, index) => (
                        <div key={index} className="current-skill-item">
                          <span className="skill-name">{skill}</span>
                          <button
                            className="remove-current-skill"
                            onClick={() => toggleSkill(skill)}
                            title="Remove skill"
                          >
                            ✕
                          </button>
                        </div>
                      ))
                    ) : (
                      <p className="no-skills">No skills selected</p>
                    )}
                  </div>
                </div>

                <div className="skills-section">
                  <h4>➕ Add Skills</h4>
                  <div className="available-skills">
                    {availableSkills
                      .filter((skill) => !userSkills.includes(skill))
                      .map((skill, index) => (
                        <div
                          key={index}
                          className="available-skill-item"
                          onClick={() => toggleSkill(skill)}
                        >
                          <span className="skill-name">{skill}</span>
                          <span className="add-skill-btn">+</span>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button className="cancel-btn" onClick={closeSkillsModal}>
                  Cancel
                </button>
                <button className="save-btn" onClick={saveSkills}>
                  Save Skills ({userSkills.length})
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
