from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import uuid
from datetime import datetime

from resume_parser import ResumeParser
from question_generator import QuestionGenerator
from response_analyzer import ResponseAnalyzer
from database import SyncDatabaseManager

app = FastAPI(title="AI Interview System")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
parser = ResumeParser()
question_gen = QuestionGenerator()
analyzer = ResponseAnalyzer()

# Use sync database manager for simplicity
db_manager = SyncDatabaseManager()
db_manager.connect()

class InterviewResponse(BaseModel):
    question_id: str
    answer: str

class InterviewSession(BaseModel):
    session_id: str
    responses: List[InterviewResponse]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        print(f"Processing file: {file.filename}")
        content = await file.read()
        parsed_data = parser.parse(content, file.filename)
        print(f"Parsed data: {parsed_data}")
        
        # Check for duplicate email
        email = parsed_data.get('email')
        if email:
            existing_resume = db_manager.db.resumes.find_one({"parsed_data.email": email})
            if existing_resume:
                return {
                    "statusCode": 400,
                    "success": False,
                    "message": f"Resume with email {email} already exists",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "path": "/upload-resume"
                }
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        print(f"Generated session ID: {session_id}")
        
        # Save to MongoDB using sync method
        print("Saving to MongoDB...")
        resume_id = db_manager.save_parsed_resume(
            resume_data=parsed_data,
            filename=file.filename,
            session_id=session_id
        )
        print(f"Resume saved with ID: {resume_id}")
        
        # Generate questions
        questions = question_gen.generate_questions(parsed_data)
        
        return {
            "statusCode": 200,
            "success": True,
            "message": "Resume uploaded and parsed successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": "/upload-resume",
            "data": {
                "session_id": session_id,
                "resume_id": resume_id,
                "parsed_resume": parsed_data,
                "questions": questions
            }
        }
        
    except Exception as e:
        print(f"Error in upload_resume: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "success": False,
            "message": f"Error processing resume: {str(e)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": "/upload-resume"
        }

@app.post("/submit-interview")
async def submit_interview(session: InterviewSession):
    try:
        score = analyzer.analyze_responses(session.responses)
        
        # Update interview session with results
        update_data = {
            "responses": [response.dict() for response in session.responses],
            "score": score,
            "status": "completed",
            "feedback": "Interview completed"
        }
        
        # Note: This assumes session_id is actually the interview_id
        # You might need to adjust based on your session management
        await db_manager.update_interview_session(session.session_id, update_data)
        
        return {
            "score": score, 
            "feedback": "Interview completed",
            "session_id": session.session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting interview: {str(e)}")

@app.get("/resume/{resume_id}")
async def get_resume(resume_id: str):
    """Get resume data by ID"""
    try:
        resume = await db_manager.get_resume_by_id(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resume: {str(e)}")

@app.get("/resumes")
async def get_all_resumes():
    """Get all resumes"""
    try:
        # Get resumes from MongoDB
        collection = db_manager.db.resumes
        resumes = list(collection.find().sort("created_at", -1).limit(50))
        
        # Convert ObjectId to string
        for resume in resumes:
            resume["_id"] = str(resume["_id"])
        
        return {"resumes": resumes, "count": len(resumes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resumes: {str(e)}")

@app.get("/session/{session_id}/resumes")
async def get_session_resumes(session_id: str):
    """Get all resumes for a specific session"""
    try:
        resumes = await db_manager.get_resumes_by_session(session_id)
        return {"session_id": session_id, "resumes": resumes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session resumes: {str(e)}")

class SearchCriteria(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    skills: Optional[List[str]] = None

@app.post("/search-resumes")
async def search_resumes(criteria: SearchCriteria):
    """Search resumes based on criteria"""
    try:
        search_dict = {k: v for k, v in criteria.dict().items() if v is not None}
        resumes = await db_manager.search_resumes(search_dict)
        return {"criteria": search_dict, "resumes": resumes, "count": len(resumes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching resumes: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        if db_manager.client:
            db_manager.client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {"status": "healthy", "database": db_status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)