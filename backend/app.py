"""
Main Flask application for Smart B-roll Inserter API.
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json
from typing import Dict, List

from utils.transcript_extractor import TranscriptExtractor
from utils.broll_analyzer import BrollAnalyzer
from utils.semantic_matcher import SemanticMatcher
from utils.video_renderer import VideoRenderer

# Load environment variables
# override=True ensures .env file takes precedence over system env vars
load_dotenv(override=True)

app = Flask(__name__)

# Configure CORS - allow all origins in production, or specify your Vercel domain
# For production, update with your Vercel URL
allowed_origins = [
    "http://localhost:3000",
    "https://smart-broll-inserter.vercel.app",  # Update with your Vercel URL
    # Add more origins as needed
]

# Allow all origins for development, restrict in production
if os.getenv('FLASK_ENV') == 'production':
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
else:
    CORS(app)  # Allow all in development

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def root():
    """Root endpoint for health checks."""
    return jsonify({"status": "healthy", "service": "smart-broll-inserter-backend"}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route('/api/plan', methods=['POST'])
def generate_plan():
    """
    Main endpoint to generate B-roll insertion plan.
    
    Expects:
    - aroll: A-roll video file
    - brolls: Multiple B-roll video files
    
    Returns:
    - Timeline plan in JSON format
    """
    try:
        # Check if files are present
        if 'aroll' not in request.files:
            return jsonify({"error": "A-roll video is required"}), 400
        
        aroll_file = request.files['aroll']
        if aroll_file.filename == '':
            return jsonify({"error": "A-roll file is empty"}), 400
        
        # Get B-roll files
        broll_files = request.files.getlist('brolls')
        if not broll_files or len(broll_files) == 0:
            return jsonify({"error": "At least one B-roll clip is required"}), 400
        
        # Save uploaded files
        aroll_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(aroll_file.filename))
        aroll_file.save(aroll_path)
        
        broll_paths = []
        for broll_file in broll_files:
            if broll_file.filename:
                broll_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(broll_file.filename))
                broll_file.save(broll_path)
                broll_paths.append(broll_path)
        
        # Get parameters
        num_insertions = int(request.form.get('num_insertions', 4))
        render_video = request.form.get('render_video', 'false').lower() == 'true'
        
        # Initialize components
        openai_key = os.getenv('OPENAI_API_KEY')
        
        print("Step 1: Extracting transcript from A-roll...")
        transcript_extractor = TranscriptExtractor(model_size="base")
        transcript_data = transcript_extractor.extract_transcript(aroll_path)
        
        print("Step 2: Analyzing B-roll clips...")
        broll_analyzer = BrollAnalyzer(api_key=openai_key)
        broll_analyses = broll_analyzer.analyze_all_brolls(broll_paths)
        
        print("Step 3: Finding semantic matches...")
        semantic_matcher = SemanticMatcher(api_key=openai_key)
        insertions = semantic_matcher.find_best_matches(
            transcript_data["segments"],
            broll_analyses,
            num_insertions=num_insertions
        )
        
        # Build timeline plan
        timeline_plan = {
            "aroll_duration_sec": transcript_data["duration_sec"],
            "transcript": {
                "full_text": transcript_data["full_text"],
                "language": transcript_data["language"],
                "segments": transcript_data["segments"]
            },
            "broll_clips": broll_analyses,
            "insertions": insertions
        }
        
        # Save timeline plan to JSON
        plan_path = os.path.join(app.config['OUTPUT_FOLDER'], 'timeline_plan.json')
        with open(plan_path, 'w') as f:
            json.dump(timeline_plan, f, indent=2)
        
        response_data = {
            "timeline_plan": timeline_plan,
            "plan_file": plan_path
        }
        
        # Optional: Render video
        if render_video and insertions:
            print("Step 4: Rendering final video...")
            video_renderer = VideoRenderer()
            output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], 'final_video.mp4')
            rendered_path = video_renderer.render_video(
                aroll_path,
                broll_analyses,
                insertions,
                output_video_path
            )
            response_data["rendered_video"] = rendered_path
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error generating plan: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/plan/file', methods=['GET'])
def get_plan_file():
    """Get the saved timeline plan JSON file."""
    plan_path = os.path.join(app.config['OUTPUT_FOLDER'], 'timeline_plan.json')
    if os.path.exists(plan_path):
        with open(plan_path, 'r') as f:
            return jsonify(json.load(f)), 200
    return jsonify({"error": "Plan file not found"}), 404


if __name__ == '__main__':
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5002)))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
