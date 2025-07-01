from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict
import json

from resume_parser import ResumeParser
from question_generator import QuestionGenerator
from response_analyzer import ResponseAnalyzer

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
    content = await file.read()
    parsed_data = parser.parse(content, file.filename)
    questions = question_gen.generate_questions(parsed_data)
    
    return {
        "session_id": f"session_{hash(file.filename)}",
        "parsed_resume": parsed_data,
        "questions": questions
    }

@app.post("/submit-interview")
async def submit_interview(session: InterviewSession):
    score = analyzer.analyze_responses(session.responses)
    return {"score": score, "feedback": "Interview completed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)