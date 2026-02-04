---
name: video-clipper
description: Download and transcribe videos from TikTok, YouTube, or Instagram Reels to Obsidian notes
---

# Video Clipper

Use this skill when the user wants to download and transcribe a video from YouTube, TikTok, or Instagram Reels.

## How to Use

Run the script from `{baseDir}`:

```bash
python3 {baseDir}/video_clipper.py "<video_url>" "<output_directory>" [options]
```

### Arguments

- `video_url` (required): URL of the video (YouTube, TikTok, or Instagram Reel)
- `output_directory` (required): Directory to save the Obsidian note
- `--model`: Whisper model size: tiny (default), base, small, medium, large
- `--keep-audio`: Keep the downloaded MP3 file alongside the note

### Examples

```bash
# Basic usage
python3 {baseDir}/video_clipper.py "https://youtube.com/watch?v=xxx" ~/Obsidian/Clips/

# With larger model for better accuracy
python3 {baseDir}/video_clipper.py "https://tiktok.com/@user/video/123" ~/notes/ --model base

# Keep audio file
python3 {baseDir}/video_clipper.py "https://instagram.com/reel/xxx" /tmp --keep-audio
```

## Supported Platforms

- YouTube (`youtube.com`, `youtu.be`, YouTube Shorts)
- TikTok (`tiktok.com`)
- Instagram Reels (`instagram.com/reel/...`)

## Output

Creates `YYYY-MM-DD-HH-MM-SS-video-clip.md` with:
- YAML frontmatter (title, platform, creator, duration, source URL, tags)
- Clickable link to original video
- Brief summary (first 1-2 sentences)
- Full transcript

## Dependencies

Requires these CLI tools (install via Homebrew or package manager):

```bash
brew install yt-dlp ffmpeg whisper-cpp
```

Download the Whisper model (one-time):

```bash
mkdir -p ~/.cache/whisper-cpp
curl -L -o ~/.cache/whisper-cpp/ggml-tiny.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin
```
