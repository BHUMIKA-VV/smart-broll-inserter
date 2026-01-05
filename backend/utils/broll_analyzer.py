"""
Module for analyzing B-roll clips and generating descriptions.
Uses vision models or LLM to understand B-roll content.
"""
import os
from openai import OpenAI
from typing import List, Dict
import subprocess
import json


class BrollAnalyzer:
    """Analyzes B-roll clips and generates text descriptions."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the B-roll analyzer.
        
        Args:
            api_key: OpenAI API key for vision/LLM analysis
        """
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            self.client = None
    
    def extract_video_frame(self, video_path: str, timestamp: float = 1.0) -> str:
        """
        Extract a frame from video at specified timestamp.
        
        Args:
            video_path: Path to video file
            timestamp: Time in seconds to extract frame
            
        Returns:
            Path to extracted frame image
        """
        frame_path = video_path.replace('.mp4', '_frame.jpg').replace('.mov', '_frame.jpg')
        frame_path = os.path.join(os.path.dirname(video_path), os.path.basename(frame_path))
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", str(timestamp),
            "-vframes", "1",
            "-y", frame_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return frame_path
        except subprocess.CalledProcessError:
            return None
    
    def get_video_duration(self, video_path: str) -> float:
        """Get duration of video in seconds."""
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        try:
            duration = float(subprocess.check_output(cmd).decode().strip())
            return round(duration, 2)
        except:
            return 0.0
    
    def analyze_broll_clip(self, video_path: str, clip_id: str) -> Dict:
        """
        Analyze a single B-roll clip and generate description.
        
        Args:
            video_path: Path to B-roll video file
            clip_id: Unique identifier for the clip
            
        Returns:
            Dictionary with clip analysis
        """
        duration = self.get_video_duration(video_path)
        
        # Extract frames at different timestamps for better understanding
        frames = []
        timestamps = [0.5, duration / 2, duration - 0.5] if duration > 1 else [0.5]
        
        for ts in timestamps:
            if ts < duration:
                frame_path = self.extract_video_frame(video_path, ts)
                if frame_path and os.path.exists(frame_path):
                    frames.append(frame_path)
        
        # Generate description using OpenAI Vision API
        description = self._generate_description_with_vision(frames, video_path)
        
        # Clean up frame files
        for frame in frames:
            try:
                if os.path.exists(frame):
                    os.remove(frame)
            except:
                pass
        
        return {
            "broll_id": clip_id,
            "video_path": video_path,
            "duration_sec": duration,
            "description": description
        }
    
    def _generate_description_with_vision(self, frame_paths: List[str], video_path: str) -> str:
        """
        Generate description using OpenAI Vision API.
        Falls back to filename-based description if API unavailable.
        """
        if not self.client or not frame_paths:
            # Fallback: use filename to infer description
            filename = os.path.basename(video_path)
            return f"Video clip: {filename.replace('_', ' ').replace('-', ' ')}"
        
        try:
            # Prepare images for vision API
            import base64
            
            image_contents = []
            for frame_path in frame_paths[:3]:  # Limit to 3 frames
                with open(frame_path, "rb") as image_file:
                    image_contents.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"
                        }
                    })
            
            # Use GPT-4 Vision to describe the video
            response = self.client.chat.completions.create(
                model="gpt-4o",  # or "gpt-4-turbo" if gpt-4o is not available
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe what you see in these video frames. Focus on objects, actions, settings, and mood. Be specific and concise."
                            }
                        ] + image_contents
                    }
                ],
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating vision description: {e}")
            # Fallback description
            filename = os.path.basename(video_path)
            return f"Video clip showing: {filename.replace('_', ' ').replace('-', ' ')}"
    
    def analyze_all_brolls(self, broll_paths: List[str]) -> List[Dict]:
        """
        Analyze all B-roll clips.
        
        Args:
            broll_paths: List of paths to B-roll video files
            
        Returns:
            List of analysis dictionaries
        """
        analyses = []
        for idx, path in enumerate(broll_paths):
            clip_id = f"broll_{idx:02d}"
            analysis = self.analyze_broll_clip(path, clip_id)
            analyses.append(analysis)
        
        return analyses
