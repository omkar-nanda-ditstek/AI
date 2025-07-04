from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from resume_parser import ResumeParser
from question_generator import QuestionGenerator
from response_analyzer import ResponseAnalyzer
from database import SyncDatabaseManager
from ai_providers import AIManager

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
ai_provider = os.getenv("AI_PROVIDER", "ollama")
ai_manager = AIManager(ai_provider)
question_gen = QuestionGenerator(ai_manager=ai_manager)
analyzer = ResponseAnalyzer(ai_manager=ai_manager)

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

@app.get("/interview", response_class=HTMLResponse)
async def interview_page(request: Request):
    return templates.TemplateResponse("interview.html", {"request": request})

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
        print("Generating questions...")
        questions = question_gen.generate_questions(parsed_data)
        print(f"Questions generated: {questions}")
        
        response_data = {
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
        
        print(f"Returning response: {response_data}")
        return response_data
        
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

# Removed duplicate submit-interview endpoint

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

class SkillUpdate(BaseModel):
    skill: str

class SkillsUpdate(BaseModel):
    skills: List[str]

@app.post("/add-skill/{resume_id}")
async def add_skill(resume_id: str, skill_data: SkillUpdate):
    """Add a skill to resume"""
    try:
        from bson import ObjectId
        
        # Add skill to MongoDB using $addToSet to avoid duplicates
        result = db_manager.db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {
                "$addToSet": {"parsed_data.skills": skill_data.skill},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count > 0:
            return {
                "statusCode": 200,
                "success": True,
                "message": f"Skill '{skill_data.skill}' added successfully",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": f"/add-skill/{resume_id}"
            }
        else:
            return {
                "statusCode": 404,
                "success": False,
                "message": "Resume not found or skill already exists",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": f"/add-skill/{resume_id}"
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "success": False,
            "message": f"Error adding skill: {str(e)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": f"/add-skill/{resume_id}"
        }

@app.delete("/remove-skill/{resume_id}")
async def remove_skill(resume_id: str, skill_data: SkillUpdate):
    """Remove a skill from resume"""
    try:
        from bson import ObjectId
        
        # Remove skill from MongoDB
        result = db_manager.db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {
                "$pull": {"parsed_data.skills": skill_data.skill},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count > 0:
            return {
                "statusCode": 200,
                "success": True,
                "message": f"Skill '{skill_data.skill}' removed successfully",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": f"/remove-skill/{resume_id}"
            }
        else:
            return {
                "statusCode": 404,
                "success": False,
                "message": "Resume not found or skill doesn't exist",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": f"/remove-skill/{resume_id}"
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "success": False,
            "message": f"Error removing skill: {str(e)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": f"/remove-skill/{resume_id}"
        }

@app.put("/update-skills/{resume_id}")
async def update_skills(resume_id: str, skills_data: SkillsUpdate):
    """Update all skills for a resume"""
    try:
        from bson import ObjectId
        
        # Update skills in MongoDB
        result = db_manager.db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {
                "parsed_data.skills": skills_data.skills,
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            return {
                "statusCode": 200,
                "success": True,
                "message": "Skills updated successfully",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": f"/update-skills/{resume_id}"
            }
        else:
            return {
                "statusCode": 404,
                "success": False,
                "message": "Resume not found",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "path": f"/update-skills/{resume_id}"
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "success": False,
            "message": f"Error updating skills: {str(e)}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": f"/update-skills/{resume_id}"
        }

# Removed Pydantic models to fix InterviewResponse error

@app.post("/submit-interview")
async def submit_interview(request: Request):
    """Submit interview responses and save to database"""
    try:
        print(f"=== SUBMIT INTERVIEW API CALLED ===")
        
        # Get raw JSON data
        interview_data = await request.json()
        print(f"Received data: {interview_data}")
        
        session_id = interview_data.get('session_id')
        resume_id = interview_data.get('resume_id')
        responses = interview_data.get('responses', [])
        
        print(f"Session: {session_id}, Resume: {resume_id}, Responses: {len(responses)}")
        
        if not session_id or not resume_id:
            print("Missing required fields")
            return {
                "success": False,
                "message": "Missing session_id or resume_id"
            }
        
        # Create simple document
        interview_doc = {
            "session_id": session_id,
            "resume_id": resume_id,
            "responses": responses,
            "status": "completed",
            "created_at": datetime.utcnow().isoformat()
        }
        
        print(f"Attempting to save to database...")
        
        # Use sync database operations
        try:
            collection = db_manager.db.interviews
            result = collection.insert_one(interview_doc)
            interview_id = str(result.inserted_id)
            
            print(f"Interview saved successfully with ID: {interview_id}")
            
            response_data = {
                "success": True,
                "message": "Interview submitted successfully",
                "interview_id": interview_id
            }
            
            print(f"Returning response: {response_data}")
            return response_data
            
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            
            response_data = {
                "success": True,
                "message": "Interview processed (DB connection failed)",
                "interview_id": "temp_id"
            }
            
            print(f"Returning fallback response: {response_data}")
            return response_data
        
    except Exception as e:
        print(f"=== ERROR IN SUBMIT INTERVIEW ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": f"Server error: {str(e)}"
        }

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

class DynamicQuestionRequest(BaseModel):
    session_id: str
    resume_id: str
    conversation_history: List[Dict]
    current_question_index: int

@app.post("/generate-next-question")
async def generate_next_question(request: DynamicQuestionRequest):
    """Generate the next question based on conversation history"""
    try:
        print(f"=== GENERATE NEXT QUESTION API CALLED ===")
        print(f"Session: {request.session_id}, Resume: {request.resume_id}")
        print(f"Question index: {request.current_question_index}")
        print(f"Conversation history: {len(request.conversation_history)} items")
        
        # Get resume data with fallback
        resume_data = {"name": "Candidate", "skills": ["programming"], "experience": "Not specified"}
        
        try:
            from bson import ObjectId
            resume_doc = db_manager.db.resumes.find_one({"_id": ObjectId(request.resume_id)})
            
            if resume_doc:
                resume_data = resume_doc.get('parsed_data', resume_data)
                print(f"✅ Found resume data for: {resume_data.get('name', 'Unknown')}")
            else:
                print(f"⚠️  Resume not found, using fallback data")
        except Exception as e:
            print(f"⚠️  Could not fetch resume data: {str(e)}, using fallback")
        
        # Generate next question
        next_question = question_gen.generate_next_question(
            resume_data, 
            request.conversation_history, 
            request.current_question_index
        )
        
        print(f"✅ Generated question: {next_question['question'][:100]}...")
        
        return {
            "success": True,
            "question": next_question
        }
        
    except Exception as e:
        print(f"❌ Error generating next question: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": f"Error generating question: {str(e)}"
        }

@app.post("/test-generate-question")
async def test_generate_question():
    """Test endpoint for dynamic question generation"""
    try:
        # Sample conversation history for testing
        test_conversation = [
            {"question": "How are you doing today?", "answer": "I'm feeling great and excited about this interview!"},
        ]
        
        # Sample resume data
        test_resume_data = {
            "name": "Alex",
            "skills": ["JavaScript", "React", "Node.js"],
            "experience": "2 years"
        }
        
        # Generate next question
        next_question = question_gen.generate_next_question(
            test_resume_data, 
            test_conversation, 
            1
        )
        
        return {
            "success": True,
            "question": next_question,
            "test_data": {
                "conversation": test_conversation,
                "resume": test_resume_data
            }
        }
        
    except Exception as e:
        print(f"Error in test endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)