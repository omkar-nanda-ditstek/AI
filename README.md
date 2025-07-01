# AI Interview System

A resume-based interview system that generates tailored questions and analyzes responses.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

## API Endpoints

- `POST /upload-resume` - Upload resume and get questions
- `POST /submit-interview` - Submit answers and get score

## Usage

1. Upload resume (PDF/DOCX/TXT)
2. Answer generated questions
3. Receive score and feedback

## Next Steps

- Integrate OpenAI API for better analysis
- Add speech-to-text support
- Create web frontend
- Implement user authentication