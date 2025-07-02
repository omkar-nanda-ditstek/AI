# Resume Parser AI with MongoDB Integration

This project is an AI-powered resume parser that extracts information from PDF and DOCX files and stores the data in MongoDB.

## Features

- **Resume Parsing**: Extract text from PDF/DOCX files
- **AI Analysis**: Use spaCy NLP for intelligent data extraction
- **MongoDB Storage**: Store parsed resume data in MongoDB
- **RESTful API**: FastAPI-based web service
- **Search Functionality**: Search resumes by name, email, skills
- **Interview System**: Generate questions and analyze responses

## Prerequisites

1. **Python 3.8+**
2. **MongoDB** (local or cloud instance)
3. **Required Python packages** (see requirements.txt)

## MongoDB Setup

### Option 1: Local MongoDB Installation

1. **Download and Install MongoDB**:
   - Visit [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Download MongoDB Community Server for Windows
   - Install with default settings

2. **Start MongoDB Service**:
   ```bash
   # Windows (as Administrator)
   net start MongoDB
   
   # Or start manually
   "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\data\db"
   ```

3. **Verify Installation**:
   ```bash
   # Connect to MongoDB shell
   "C:\Program Files\MongoDB\Server\7.0\bin\mongosh.exe"
   ```

### Option 2: MongoDB Atlas (Cloud)

1. **Create Account**: Sign up at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Create Cluster**: Follow the setup wizard
3. **Get Connection String**: Copy the connection string
4. **Update Configuration**: Set the `MONGODB_URL` environment variable

## Installation

1. **Clone/Navigate to Project Directory**:
   ```bash
   cd "C:\Users\Ditsd\OneDrive\Desktop\ResumeParserAI\AI"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy Model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Download NLTK Data**:
   ```bash
   python download_nltk_data.py
   ```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/
DATABASE_NAME=resume_parser_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB
```

### Database Setup

1. **Setup Database Indexes**:
   ```bash
   python setup_database.py
   ```

2. **Test MongoDB Connection**:
   ```bash
   python test_mongodb.py
   ```

## Usage

### 1. Start the API Server

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

### 2. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

### 3. API Endpoints

#### Upload Resume
```bash
POST /upload-resume
Content-Type: multipart/form-data

# Upload a PDF or DOCX file
curl -X POST "http://localhost:8000/upload-resume" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@resume.pdf"
```

#### Get Resume by ID
```bash
GET /resume/{resume_id}

curl -X GET "http://localhost:8000/resume/60f7b3b3b3b3b3b3b3b3b3b3"
```

#### Get All Resumes
```bash
GET /resumes?limit=10&skip=0

curl -X GET "http://localhost:8000/resumes?limit=10&skip=0"
```

#### Search Resumes
```bash
POST /search-resumes
Content-Type: application/json

curl -X POST "http://localhost:8000/search-resumes" \
     -H "Content-Type: application/json" \
     -d '{"name": "John", "skills": ["Python", "JavaScript"]}'
```

### 4. Test Scripts

#### Test PDF Parsing
```bash
python simple_test.py
```

#### Test MongoDB Integration
```bash
python test_mongodb.py
```

## Database Schema

### Resumes Collection
```json
{
  "_id": "ObjectId",
  "filename": "resume.pdf",
  "session_id": "uuid",
  "parsed_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "skills": ["Python", "JavaScript"],
    "experience": "3 years",
    "education": ["Bachelor's Degree"],
    "projects": ["Project 1", "Project 2"]
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Interview Sessions Collection
```json
{
  "_id": "ObjectId",
  "session_id": "uuid",
  "resume_id": "ObjectId",
  "questions": [...],
  "responses": [...],
  "score": 85,
  "status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Troubleshooting

### MongoDB Connection Issues

1. **Check MongoDB Service**:
   ```bash
   # Windows
   sc query MongoDB
   ```

2. **Check Port Availability**:
   ```bash
   netstat -an | findstr :27017
   ```

3. **Firewall Settings**: Ensure port 27017 is open

### Common Errors

1. **"No module named 'pymongo'"**: Run `pip install pymongo motor`
2. **"Connection refused"**: Start MongoDB service
3. **"Authentication failed"**: Check MongoDB credentials
4. **"Database not found"**: Database will be created automatically

## Performance Optimization

1. **Indexes**: Run `setup_database.py` to create indexes
2. **Connection Pooling**: Configured in `database.py`
3. **File Size Limits**: Configured in `config.py`

## Security Considerations

1. **Authentication**: Enable MongoDB authentication in production
2. **Network Security**: Use VPN or private networks
3. **Data Encryption**: Enable encryption at rest and in transit
4. **Input Validation**: All inputs are validated by Pydantic models

## Monitoring

### Database Statistics
```python
# Connect to MongoDB shell
use resume_parser_db
db.stats()
db.resumes.count()
db.interview_sessions.count()
```

### API Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

## Support

For issues and questions:
1. Check the logs in the console output
2. Verify MongoDB connection
3. Ensure all dependencies are installed
4. Check the API documentation at `/docs`