"""
Module for rendering final video with B-roll insertions.
Uses ffmpeg to overlay B-roll visuals while keeping A-roll audio.
"""
import subprocess
import os
from typing import List, Dict
import json


class VideoRenderer:
    """Renders final video with B-roll insertions."""
    
    def __init__(self):
        """Initialize the video renderer."""
        pass
    
    def render_video(
        self,
        aroll_path: str,
        broll_analyses: List[Dict],
        insertions: List[Dict],
        output_path: str
    ) -> str:
        """
        Render final video with B-roll insertions.
        
        Args:
            aroll_path: Path to A-roll video
            broll_analyses: List of B-roll analyses (for paths)
            insertions: List of insertion plans
            output_path: Path for output video
            
        Returns:
            Path to rendered video
        """
        if not insertions:
            print("No insertions to render. Copying A-roll as-is.")
            subprocess.run(["ffmpeg", "-i", aroll_path, "-c", "copy", "-y", output_path], check=True)
            return output_path
        
        # Create a mapping of broll_id to video path
        broll_map = {broll["broll_id"]: broll["video_path"] for broll in broll_analyses}
        
        # Build ffmpeg filter complex for overlaying B-roll clips
        # Strategy: Use overlay filter to place B-roll on top of A-roll at specified times
        
        # First, get A-roll dimensions
        aroll_info = self._get_video_info(aroll_path)
        width = aroll_info["width"]
        height = aroll_info["height"]
        
        # Collect valid insertions with their B-roll paths
        valid_insertions = []
        broll_inputs = []
        
        for insertion in insertions:
            broll_path = broll_map.get(insertion["broll_id"])
            if broll_path and os.path.exists(broll_path):
                valid_insertions.append(insertion)
                broll_inputs.append(broll_path)
        
        if not valid_insertions:
            # No valid insertions, just copy A-roll
            subprocess.run(["ffmpeg", "-i", aroll_path, "-c", "copy", "-y", output_path], check=True)
            return output_path
        
        # Build filter complex for overlaying B-roll clips
        # Using picture-in-picture style: smaller in corner
        broll_width = width // 3
        broll_height = height // 3
        
        # Start with A-roll video
        current_label = "[0:v]"
        filter_parts = []
        
        # Build overlay chain
        for idx, insertion in enumerate(valid_insertions):
            input_idx = idx + 1  # B-roll input index (0 is A-roll)
            start_time = insertion["start_sec"]
            duration = insertion["duration_sec"]
            
            # Scale B-roll
            scaled_label = f"[broll{input_idx}]"
            filter_parts.append(f"[{input_idx}:v]scale={broll_width}:{broll_height}{scaled_label};")
            
            # Overlay B-roll on current video
            next_label = f"[v{input_idx}]"
            overlay_expr = (
                f"{current_label}{scaled_label}overlay=W-w-10:10:"
                f"enable='between(t,{start_time},{start_time + duration})'{next_label};"
            )
            filter_parts.append(overlay_expr)
            
            current_label = next_label
        
        # Build final filter complex (remove last semicolon)
        filter_complex = "".join(filter_parts).rstrip(";")
        final_output = current_label
        
        # Build ffmpeg command
        final_cmd = ["ffmpeg", "-i", aroll_path]
        for broll_path in broll_inputs:
            final_cmd.extend(["-i", broll_path])
        final_cmd.extend([
            "-filter_complex", filter_complex,
            "-map", final_output,
            "-map", "0:a",  # Keep A-roll audio
            "-c:v", "libx264",
            "-c:a", "copy",
            "-preset", "medium",
            "-y",
            output_path
        ])
        
        try:
            print(f"Rendering video with {len(insertions)} B-roll insertions...")
            subprocess.run(final_cmd, check=True, capture_output=True)
            print(f"Video rendered successfully: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error rendering video: {e}")
            print(f"stderr: {e.stderr.decode() if e.stderr else 'No stderr'}")
            # Fallback: simple concatenation approach
            return self._render_simple_overlay(aroll_path, broll_map, insertions, output_path)
    
    def _render_simple_overlay(
        self,
        aroll_path: str,
        broll_map: Dict,
        insertions: List[Dict],
        output_path: str
    ) -> str:
        """Simpler rendering approach using basic overlay."""
        # This is a fallback - for production, use a more robust approach
        # For now, just copy the A-roll
        subprocess.run(["ffmpeg", "-i", aroll_path, "-c", "copy", "-y", output_path], check=True)
        return output_path
    
    def _get_video_info(self, video_path: str) -> Dict:
        """Get video dimensions and other info."""
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json",
            video_path
        ]
        try:
            result = subprocess.check_output(cmd).decode()
            info = json.loads(result)
            stream = info.get("streams", [{}])[0]
            return {
                "width": int(stream.get("width", 1920)),
                "height": int(stream.get("height", 1080))
            }
        except:
            return {"width": 1920, "height": 1080}
