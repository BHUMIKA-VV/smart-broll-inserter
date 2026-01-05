# Talking Head Video Dataset Guide

This guide helps you find and download talking head videos for testing the Smart B-roll Inserter.

## Recommended Datasets

### 1. **TalkVid** ⭐ (Recommended - Large, Modern, Open)
- **Size**: ~1,244 hours of HD/4K footage
- **Speakers**: 7,729 unique speakers
- **Languages**: 15 languages
- **Format**: HD/4K videos with synchronized audio
- **Purpose**: Audio-driven talking-head synthesis and benchmarks
- **Access**: 
  - GitHub: https://github.com/FreedomIntelligence/TalkVid
  - Check the repository for download links and sample videos
  - Usually requires academic/research access or agreement to terms

### 2. **THVD (Talking Head Video Dataset)** ⭐
- **Size**: ~47,547 videos, ~2.7 TB
- **Identities**: 20,841+ unique identities
- **Resolution**: 4K / 1080p clips
- **Duration**: 20 seconds to 5 minutes (full-length videos)
- **Format**: MP4 with continuous mouth motion and speech audio
- **Purpose**: High-res faces, long segments
- **Access**: 
  - Papers with Code: https://paperswithcode.com/dataset/thvd
  - Usually requires academic/research access
  - Check research papers citing THVD for access instructions

### 3. **SpeakerVid-5M** (For Interactive Agents)
- **Size**: 5.2M audiovisual clips, ~8,743 hours
- **Content**: Monologue, listening, and dyadic conversations
- **Purpose**: Interactive "virtual human" / agent tasks with dialogue-style data
- **Access**: 
  - Check academic papers or research repositories
  - May require research affiliation

### 2. **HDTF (High-definition Talking Face Dataset)**
- **Size**: ~16 hours
- **Resolution**: 720P to 1080P
- **Subjects**: 300+ subjects
- **Format**: YouTube videos (720P-1080P)
- **Access**: 
  - Papers with Code: https://paperswithcode.com/dataset/hdtf
  - Usually available via academic/research channels

### 3. **THVD (Talking Head Video Dataset)**
- **Size**: 500+ hours, 50,000+ videos
- **Resolution**: 4K and Full HD
- **Duration**: 20 seconds to 5 minutes
- **Format**: MP4
- **Access**: Check Papers with Code or research papers citing it

### 4. **MultiTalk**
- **Size**: 423 hours
- **Languages**: 20 languages
- **Access**: https://multi-talk.github.io/

## Quick Access Methods

### Method 1: YouTube Creative Commons (Easiest)
1. Go to YouTube
2. Search for: "talking head interview" or "vlog talking to camera"
3. Filter by: Creative Commons license
4. Download using `yt-dlp` (if allowed by license)

### Method 2: Free Stock Video Sites
- **Pexels Videos**: https://www.pexels.com/videos/
  - Search: "interview", "presenter", "talking head"
- **Pixabay Videos**: https://pixabay.com/videos/
  - Search: "person speaking", "interview"

### Method 3: Academic Datasets
Many datasets require:
- Academic email or affiliation
- Research purpose statement
- Agreement to terms of use

## Using yt-dlp to Download YouTube Videos

If you find Creative Commons videos on YouTube:

```bash
# Install yt-dlp
pip install yt-dlp

# Download a video (replace URL with actual video)
yt-dlp -f "best[height<=1080]" "YOUTUBE_URL" -o "aroll_sample.mp4"

# Download with audio (important!)
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" "YOUTUBE_URL" -o "aroll_sample.mp4"
```

**Important**: Always check the license and terms of use before downloading!

## Sample Video Requirements

For A-roll videos:
- ✅ Must have audio track with speech
- ✅ Duration: 30-90 seconds (recommended)
- ✅ Format: MP4, MOV, AVI, MKV, WebM
- ✅ Resolution: 720P or higher
- ✅ Talking head format (person speaking to camera)

For B-roll videos:
- ✅ Can be silent (no audio required)
- ✅ Duration: 5-20 seconds each
- ✅ Multiple clips (6+ recommended)
- ✅ Various visual content

## Quick Test Setup

1. **Download 1 A-roll video** (30-60 seconds, with audio)
2. **Download 4-6 B-roll clips** (5-15 seconds each)
3. Upload to the Smart B-roll Inserter UI
4. Generate plan!

## Legal Notes

- Always respect copyright and licensing
- Use Creative Commons or public domain content when possible
- For commercial use, ensure proper licensing
- Academic datasets often have research-only restrictions
