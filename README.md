# Smart B-roll Inserter

An intelligent system that automatically plans B-roll clip insertions into A-roll (talking-head) videos using semantic matching and AI-powered analysis.

## Overview

This system analyzes A-roll videos to extract transcripts with timestamps, analyzes B-roll clips to understand their content, and uses semantic matching to automatically determine where and which B-roll clips should be inserted for optimal visual storytelling.

## Features

- **A-roll Analysis**: Extracts transcripts with sentence-level timestamps using OpenAI Whisper
- **B-roll Analysis**: Generates descriptions of B-roll clips using vision models
- **Semantic Matching**: Uses sentence transformers to match transcript segments with appropriate B-roll clips
- **Timeline Planning**: Generates structured JSON timeline plans with insertion points
- **Video Rendering** (Optional): Renders final video with B-roll overlays using ffmpeg
- **React Frontend**: User-friendly interface for uploading videos and viewing results

## Tech Stack

- **Backend**: Python, Flask, OpenAI Whisper, OpenAI API, Sentence Transformers, ffmpeg
- **Frontend**: React, Axios
- **AI/ML**: OpenAI GPT-4 Vision, Whisper, Sentence Transformers (all-MiniLM-L6-v2)

## Prerequisites

- Python 3.8+
- Node.js 16+
- ffmpeg installed and available in PATH
- OpenAI API key (for B-roll analysis and LLM-based reasoning)

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 3. Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The backend will run on `http://localhost:5000`

### Start Frontend

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000` and automatically proxy API requests to the backend.

## Usage

1. **Upload Videos**:
   - Select an A-roll video (talking-head video, 30-90 seconds recommended)
   - Select multiple B-roll clips (6 clips recommended)
   - Configure number of insertions (3-6 recommended)
   - Optionally enable video rendering

2. **Generate Plan**:
   - Click "Generate B-roll Plan"
   - Wait for processing (may take a few minutes)

3. **View Results**:
   - View the extracted transcript with timestamps
   - Review the timeline plan with insertion points
   - See semantic matching reasons for each insertion

## API Endpoints

### `POST /api/plan`

Generate B-roll insertion plan.

**Request:**
- `aroll`: A-roll video file (multipart/form-data)
- `brolls`: Multiple B-roll video files (multipart/form-data)
- `num_insertions`: Number of insertions (form field, default: 4)
- `render_video`: Whether to render final video (form field, default: false)

**Response:**
```json
{
  "timeline_plan": {
    "aroll_duration_sec": 45.2,
    "transcript": {
      "full_text": "...",
      "segments": [...]
    },
    "broll_clips": [...],
    "insertions": [
      {
        "start_sec": 12.5,
        "duration_sec": 2.0,
        "broll_id": "broll_03",
        "confidence": 0.78,
        "reason": "..."
      }
    ]
  },
  "plan_file": "outputs/timeline_plan.json",
  "rendered_video": "outputs/final_video.mp4"  // if render_video=true
}
```

### `GET /api/plan/file`

Get the saved timeline plan JSON file.

## Project Structure

```
smart-broll-inserter/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── uploads/              # Uploaded video files
│   ├── outputs/              # Generated plans and videos
│   └── utils/
│       ├── transcript_extractor.py    # Whisper-based transcription
│       ├── broll_analyzer.py          # B-roll clip analysis
│       ├── semantic_matcher.py       # Semantic matching logic
│       └── video_renderer.py          # ffmpeg video rendering
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── components/
│   │   │   ├── FileUpload.js
│   │   │   ├── TranscriptViewer.js
│   │   │   └── TimelineViewer.js
│   │   └── services/         # API service functions
│   └── package.json
└── README.md
```

## How It Works

1. **Transcript Extraction**: Uses OpenAI Whisper to extract speech from A-roll video with word-level timestamps, then groups into sentence-level segments.

2. **B-roll Analysis**: Extracts frames from B-roll clips at different timestamps and uses GPT-4 Vision API to generate descriptions of what each clip shows.

3. **Semantic Matching**: 
   - Computes embeddings for transcript segments and B-roll descriptions using sentence transformers
   - Calculates cosine similarity between embeddings
   - Selects best matches while respecting constraints (minimum gaps, avoiding critical speaking moments)

4. **Timeline Planning**: Generates structured JSON plan with insertion points, durations, and reasoning.

5. **Video Rendering** (Optional): Uses ffmpeg to overlay B-roll clips onto A-roll at specified timestamps while preserving A-roll audio.

## Constraints & Design Decisions

- **Minimum gap between insertions**: 3 seconds (configurable)
- **Insertion duration**: Typically 2-2.5 seconds, limited by clip duration
- **Avoids insertions**: During very short segments (< 1s) or at the very beginning (< 2s)
- **Matching strategy**: Semantic similarity with embedding-based cosine similarity
- **Fallback handling**: Graceful degradation if OpenAI API is unavailable

## Environment Variables

Required in `backend/.env`:
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4 Vision and GPT-3.5-turbo

Optional:
- `FLASK_ENV`: Development or production (default: development)
- `FLASK_PORT`: Backend port (default: 5000)

## Limitations & Future Improvements

- Current implementation uses picture-in-picture style overlays; could support full-screen transitions
- Video rendering is basic; could add transitions, effects, and better compositing
- B-roll analysis uses static frames; could analyze motion and action
- Matching logic could be enhanced with more sophisticated NLP techniques
- Could add support for custom insertion rules and preferences

## Troubleshooting

**ffmpeg not found**: Ensure ffmpeg is installed and in your PATH. Test with `ffmpeg -version`.

**OpenAI API errors**: Check your API key is set correctly and you have sufficient credits.

**Large file uploads**: Increase `MAX_CONTENT_LENGTH` in `app.py` if needed.

**Whisper model download**: First run will download the Whisper model (~150MB for base model).

## License

This project is created for assignment purposes.

## Acknowledgments

- OpenAI Whisper for speech recognition
- OpenAI GPT-4 Vision for image understanding
- Sentence Transformers for semantic embeddings
- ffmpeg for video processing
