---
name: video-clipper
description: Download and transcribe videos from TikTok, YouTube, or Instagram Reels to Obsidian notes
version: 1.0.0
author: iceycake
invoke: ./video_clipper.py
args:
  - name: url
    description: URL of the video (YouTube, TikTok, or Instagram Reel)
    required: true
  - name: output_directory
    description: Directory to save the Obsidian note
    required: true
  - name: --model
    description: "Whisper model size: tiny, base, small, medium, large"
    default: base
  - name: --keep-audio
    description: Keep the downloaded audio file alongside the note
    default: false
tags:
  - video
  - transcription
  - obsidian
  - youtube
  - tiktok
  - instagram
---

# video-clipper

Download and transcribe videos from TikTok, YouTube, or Instagram Reels, creating an Obsidian note with metadata and full transcript.

## When to Use

Use this skill when the user wants to:
- Download and transcribe a video from YouTube, TikTok, or Instagram
- Create an Obsidian note from a video
- Get a transcript of a social media video
- Save a video clip with notes

## Supported Platforms

- YouTube (`youtube.com`, `youtu.be`, YouTube Shorts)
- TikTok (`tiktok.com`)
- Instagram Reels (`instagram.com/reel/...`)

## Output

Creates `YYYY-MM-DD-HH-MM-SS-video-clip.md` with:
- YAML frontmatter (title, platform, creator, duration, source URL, tags)
- Clickable link to original video
- 1-2 sentence summary
- Full transcript

## Examples

```bash
# Basic usage
./video_clipper.py "https://youtube.com/watch?v=xxx" ~/Obsidian/Clips/

# With larger model for better accuracy
./video_clipper.py "https://tiktok.com/@user/video/123" ~/Obsidian/Clips/ --model medium

# Keep audio file
./video_clipper.py "https://instagram.com/reel/xxx" ~/Obsidian/Clips/ --keep-audio
```

## Setup

```bash
cd video-clipper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Requires `ffmpeg` for audio extraction (`brew install ffmpeg`).
