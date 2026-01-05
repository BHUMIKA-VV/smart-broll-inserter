"""
Module for extracting transcripts from A-roll videos with timestamps.
Uses OpenAI Whisper for speech-to-text transcription.
"""
import whisper
import json
from typing import List, Dict


class TranscriptExtractor:
    """Extracts transcript with timestamps from video files."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the transcript extractor.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
    
    def _has_audio_stream(self, video_path: str) -> bool:
        """Check if video file has an audio stream."""
        import subprocess
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=codec_type", "-of", "csv=p=0",
            video_path
        ]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            return output == "audio"
        except:
            return False
    
    def extract_transcript(self, video_path: str) -> Dict:
        """
        Extract transcript with timestamps from A-roll video.
        
        Args:
            video_path: Path to the A-roll video file
            
        Returns:
            Dictionary containing transcript segments with timestamps
        """
        # Check if video has audio stream
        if not self._has_audio_stream(video_path):
            raise ValueError(
                "The video file does not contain an audio track. "
                "Please use a video file with audio for A-roll transcription. "
                "A-roll videos should be talking-head videos with speech."
            )
        
        print(f"Transcribing video: {video_path}")
        try:
            result = self.model.transcribe(video_path, word_timestamps=True)
        except Exception as e:
            error_msg = str(e)
            if "audio" in error_msg.lower() or "stream" in error_msg.lower():
                raise ValueError(
                    "Failed to extract audio from video. "
                    "The video file may not have an audio track. "
                    "Please ensure your A-roll video contains audio with speech."
                ) from e
            raise
        
        # Get video duration
        import subprocess
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        try:
            duration = float(subprocess.check_output(duration_cmd).decode().strip())
        except:
            duration = 0.0
        
        # Process segments into sentence-level chunks
        segments = []
        current_sentence = ""
        current_start = None
        current_end = None
        
        for segment in result["segments"]:
            text = segment["text"].strip()
            start = segment["start"]
            end = segment["end"]
            
            # Simple sentence splitting (can be improved)
            if current_sentence:
                current_sentence += " " + text
                current_end = end
            else:
                current_sentence = text
                current_start = start
                current_end = end
            
            # Check if we have a complete sentence (ends with punctuation)
            if text and text[-1] in ".!?":
                segments.append({
                    "text": current_sentence,
                    "start_sec": round(current_start, 2),
                    "end_sec": round(current_end, 2),
                    "duration_sec": round(current_end - current_start, 2)
                })
                current_sentence = ""
                current_start = None
                current_end = None
        
        # Add any remaining text
        if current_sentence:
            segments.append({
                "text": current_sentence,
                "start_sec": round(current_start, 2),
                "end_sec": round(current_end, 2),
                "duration_sec": round(current_end - current_start, 2)
            })
        
        return {
            "full_text": result["text"],
            "language": result.get("language", "en"),
            "duration_sec": round(duration, 2),
            "segments": segments
        }
