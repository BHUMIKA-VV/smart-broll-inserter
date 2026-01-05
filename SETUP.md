# Quick Setup Guide

## Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp env_template.txt .env
# Edit .env and add your OPENAI_API_KEY
```

## Step 2: Frontend Setup

```bash
cd frontend
npm install
```

## Step 3: Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Step 4: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Open http://localhost:3000 in your browser.

## Notes

- First run will download Whisper model (~150MB)
- Ensure ffmpeg is in your PATH: `ffmpeg -version`
- OpenAI API key is required for B-roll analysis (reimbursable per assignment)
