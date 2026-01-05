"""
Module for semantic matching between A-roll transcript and B-roll clips.
Uses sentence transformers for embedding-based similarity matching.
"""
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple
from openai import OpenAI


class SemanticMatcher:
    """Matches A-roll transcript segments with appropriate B-roll clips."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the semantic matcher.
        
        Args:
            api_key: OpenAI API key (optional, for LLM-based matching)
        """
        print("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            self.client = None
    
    def compute_embeddings(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for a list of texts."""
        return self.model.encode(texts)
    
    def find_best_matches(
        self,
        transcript_segments: List[Dict],
        broll_analyses: List[Dict],
        num_insertions: int = 4,
        min_gap_seconds: float = 3.0
    ) -> List[Dict]:
        """
        Find best B-roll matches for transcript segments.
        
        Args:
            transcript_segments: List of transcript segments with timestamps
            broll_analyses: List of B-roll clip analyses
            num_insertions: Target number of B-roll insertions
            min_gap_seconds: Minimum gap between insertions
            
        Returns:
            List of insertion plans
        """
        # Prepare texts for embedding
        segment_texts = [seg["text"] for seg in transcript_segments]
        broll_texts = [analysis["description"] for analysis in broll_analyses]
        
        # Compute embeddings
        segment_embeddings = self.compute_embeddings(segment_texts)
        broll_embeddings = self.compute_embeddings(broll_texts)
        
        # Compute similarity matrix
        similarity_matrix = cosine_similarity(segment_embeddings, broll_embeddings)
        
        # Find best matches
        insertions = []
        used_segments = set()
        used_brolls = set()
        last_insertion_time = -min_gap_seconds
        
        # Sort potential matches by similarity
        candidates = []
        for seg_idx, segment in enumerate(transcript_segments):
            for broll_idx, broll in enumerate(broll_analyses):
                similarity = similarity_matrix[seg_idx, broll_idx]
                candidates.append({
                    "segment": segment,
                    "broll": broll,
                    "similarity": similarity,
                    "segment_idx": seg_idx,
                    "broll_idx": broll_idx
                })
        
        # Sort by similarity (descending)
        candidates.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Select insertions with constraints
        for candidate in candidates:
            if len(insertions) >= num_insertions:
                break
            
            segment = candidate["segment"]
            broll = candidate["broll"]
            seg_start = segment["start_sec"]
            
            # Check constraints
            if (seg_start - last_insertion_time < min_gap_seconds or
                candidate["segment_idx"] in used_segments or
                candidate["broll_idx"] in used_brolls):
                continue
            
            # Avoid inserting during very short segments or at the very beginning
            if seg_start < 2.0 or segment["duration_sec"] < 1.0:
                continue
            
            # Determine insertion timing (middle of segment)
            insertion_start = seg_start + (segment["duration_sec"] / 3)
            insertion_duration = min(2.5, broll["duration_sec"], segment["duration_sec"] * 0.6)
            
            # Generate reason using LLM if available
            reason = self._generate_insertion_reason(
                segment["text"],
                broll["description"],
                candidate["similarity"]
            )
            
            insertions.append({
                "start_sec": round(insertion_start, 2),
                "duration_sec": round(insertion_duration, 2),
                "broll_id": broll["broll_id"],
                "confidence": round(float(candidate["similarity"]), 2),
                "reason": reason
            })
            
            used_segments.add(candidate["segment_idx"])
            used_brolls.add(candidate["broll_idx"])
            last_insertion_time = insertion_start + insertion_duration
        
        # Sort insertions by timestamp
        insertions.sort(key=lambda x: x["start_sec"])
        
        return insertions
    
    def _generate_insertion_reason(
        self,
        segment_text: str,
        broll_description: str,
        similarity: float
    ) -> str:
        """Generate a human-readable reason for the insertion."""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a video editor explaining why a B-roll clip matches a specific moment in dialogue. Be concise (one sentence)."
                        },
                        {
                            "role": "user",
                            "content": f"Dialogue: '{segment_text}'\nB-roll shows: '{broll_description}'\nSimilarity score: {similarity:.2f}\nWhy does this B-roll match this moment?"
                        }
                    ],
                    max_tokens=50
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error generating LLM reason: {e}")
        
        # Fallback reason
        return f"B-roll content ({broll_description[:50]}...) semantically matches the dialogue about {segment_text[:30]}..."
