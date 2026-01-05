#!/usr/bin/env python3
"""
Helper script to download sample talking head videos for testing.
Supports YouTube (Creative Commons) and provides guidance for other sources.
"""

import os
import sys
import subprocess
import argparse

def check_yt_dlp():
    """Check if yt-dlp is installed."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_yt_dlp():
    """Install yt-dlp if not available."""
    print("Installing yt-dlp...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
        print("✓ yt-dlp installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install yt-dlp. Please install manually: pip install yt-dlp")
        return False

def download_youtube_video(url, output_dir="sample_videos", quality="720p"):
    """Download a YouTube video (Creative Commons only!)."""
    if not check_yt_dlp():
        print("yt-dlp not found. Installing...")
        if not install_yt_dlp():
            return None
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Download with audio (important for A-roll)
    cmd = [
        "yt-dlp",
        "-f", f"bestvideo[height<={quality.replace('p', '')}]+bestaudio/best[height<={quality.replace('p', '')}]",
        "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
        url
    ]
    
    print(f"Downloading video from: {url}")
    print("⚠️  WARNING: Only download Creative Commons or public domain videos!")
    print("⚠️  Check the video license before downloading.\n")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✓ Video downloaded to {output_dir}/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error downloading video: {e}")
        return False

def print_sources():
    """Print information about video sources."""
    print("\n" + "="*60)
    print("RECOMMENDED SOURCES FOR TALKING HEAD VIDEOS")
    print("="*60)
    print("\n1. PEXELS VIDEOS (Free, No Attribution Required)")
    print("   URL: https://www.pexels.com/videos/")
    print("   Search: 'interview', 'presenter', 'talking head'")
    print("   License: Free for commercial use")
    
    print("\n2. PIXABAY VIDEOS (Free)")
    print("   URL: https://pixabay.com/videos/")
    print("   Search: 'person speaking', 'interview', 'presenter'")
    print("   License: Free for commercial use")
    
    print("\n3. YOUTUBE CREATIVE COMMONS")
    print("   - Go to YouTube")
    print("   - Search for talking head videos")
    print("   - Filter by 'Creative Commons' license")
    print("   - Use yt-dlp to download (if allowed)")
    print("   ⚠️  Always check license before downloading!")
    
    print("\n4. TALKVID DATASET ⭐ (Large, Modern, Open)")
    print("   Size: ~1,244 hours, 7,729 speakers, HD/4K")
    print("   GitHub: https://github.com/FreedomIntelligence/TalkVid")
    print("   Check repository for download links and access")
    
    print("\n5. THVD (Talking Head Video Dataset) ⭐")
    print("   Size: ~47,547 videos, ~2.7 TB, 20k+ identities")
    print("   Resolution: 4K / 1080p, 20 sec - 5 min clips")
    print("   Papers with Code: https://paperswithcode.com/dataset/thvd")
    print("   Usually requires academic/research access")
    
    print("\n6. SPEAKERVID-5M (For Interactive Agents)")
    print("   Size: 5.2M clips, ~8,743 hours")
    print("   Content: Monologue, listening, dyadic conversations")
    print("   Check academic papers for access")
    
    print("\n" + "="*60)
    print("QUICK TEST SETUP")
    print("="*60)
    print("\n1. Download 1 A-roll video (30-60 seconds, WITH AUDIO)")
    print("2. Download 4-6 B-roll clips (5-15 seconds each)")
    print("3. Upload to Smart B-roll Inserter UI")
    print("4. Generate plan!\n")

def main():
    parser = argparse.ArgumentParser(
        description="Download sample videos for Smart B-roll Inserter testing"
    )
    parser.add_argument(
        "--youtube-url",
        type=str,
        help="YouTube URL to download (Creative Commons only!)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="sample_videos",
        help="Output directory for downloaded videos (default: sample_videos)"
    )
    parser.add_argument(
        "--quality",
        type=str,
        default="720p",
        choices=["480p", "720p", "1080p"],
        help="Video quality (default: 720p)"
    )
    parser.add_argument(
        "--sources",
        action="store_true",
        help="Show recommended video sources"
    )
    
    args = parser.parse_args()
    
    if args.sources:
        print_sources()
    elif args.youtube_url:
        print("⚠️  IMPORTANT: Only download Creative Commons or public domain videos!")
        response = input("Have you verified the video license? (yes/no): ")
        if response.lower() != "yes":
            print("Please verify the license first. Exiting.")
            return
        
        download_youtube_video(args.youtube_url, args.output_dir, args.quality)
    else:
        print("Smart B-roll Inserter - Sample Video Downloader\n")
        print_sources()
        print("\nUsage examples:")
        print("  python scripts/download_samples.py --sources")
        print("  python scripts/download_samples.py --youtube-url 'URL' --output-dir samples")

if __name__ == "__main__":
    main()
