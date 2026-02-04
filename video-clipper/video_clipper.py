#!/Users/achan/Projects/com/github/iceycake/skills/video-clipper/venv/bin/python
"""
Video Clipper - Download and transcribe videos from TikTok, YouTube, or Instagram Reels.
Creates an Obsidian note with metadata, summary, and full transcript.
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
import whisper


def detect_platform(url: str) -> str:
    """Detect the video platform from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    if "tiktok.com" in domain or "tiktok" in domain:
        return "tiktok"
    elif "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    elif "instagram.com" in domain and "/reel" in path:
        return "reel"
    elif "instagram.com" in domain:
        return "reel"  # Assume Instagram links are reels
    else:
        raise ValueError(f"Unsupported platform for URL: {url}")


def download_video(url: str, output_dir: str) -> tuple[str, dict]:
    """Download video and return path to audio file and video metadata."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id", "video")
        audio_path = os.path.join(output_dir, f"{video_id}.mp3")

        metadata = {
            "title": info.get("title", "Untitled"),
            "uploader": info.get("uploader", "Unknown"),
            "upload_date": info.get("upload_date", ""),
            "duration": info.get("duration", 0),
            "description": info.get("description", ""),
            "view_count": info.get("view_count", 0),
            "like_count": info.get("like_count", 0),
        }

        return audio_path, metadata


def transcribe_audio(audio_path: str, model_name: str = "base") -> str:
    """Transcribe audio file using Whisper."""
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print("Transcribing audio...")
    result = model.transcribe(audio_path)

    return result["text"].strip()


def generate_summary(transcript: str, max_sentences: int = 2) -> str:
    """Generate a simple summary from the transcript (first few sentences)."""
    # Simple approach: take first 1-2 sentences
    sentences = re.split(r"(?<=[.!?])\s+", transcript)
    summary_sentences = sentences[: min(max_sentences, len(sentences))]
    return " ".join(summary_sentences)


def format_date(date_str: str) -> str:
    """Format date string from YYYYMMDD to YYYY-MM-DD."""
    if date_str and len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    return datetime.now().strftime("%Y-%m-%d")


def create_obsidian_note(
    url: str,
    platform: str,
    metadata: dict,
    transcript: str,
    summary: str,
    output_dir: str,
    timestamp: datetime,
) -> str:
    """Create an Obsidian markdown note with YAML frontmatter."""
    title = metadata.get("title", "Untitled Video")
    uploader = metadata.get("uploader", "Unknown")
    upload_date = format_date(metadata.get("upload_date", ""))
    duration = metadata.get("duration", 0)
    created_date = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # Format duration as MM:SS or HH:MM:SS
    if duration:
        hours, remainder = divmod(int(duration), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            duration_str = f"{minutes:02d}:{seconds:02d}"
    else:
        duration_str = "Unknown"

    # Build the note content
    note_content = f"""---
title: "{title.replace('"', "'")}"
platform: {platform}
creator: "{uploader.replace('"', "'")}"
upload_date: {upload_date}
duration: "{duration_str}"
source_url: "{url}"
created: {created_date}
tags:
  - video-clip
  - {platform}
---

# {title}

## Source

[Watch Original Video]({url})

**Platform:** {platform.capitalize()}
**Creator:** {uploader}
**Duration:** {duration_str}

## Summary

{summary}

## Transcript

{transcript}
"""

    # Determine output file path (always use timestamp-based filename)
    output_dir = Path(output_dir)
    filename = timestamp.strftime("%Y-%m-%d-%H-%M-%S-video-clip.md")
    file_path = output_dir / filename

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the note
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    return str(file_path)


def main():
    parser = argparse.ArgumentParser(
        description="Download and transcribe videos from TikTok, YouTube, or Instagram Reels"
    )
    parser.add_argument("url", help="URL of the video to download and transcribe")
    parser.add_argument(
        "output_path",
        help="Directory to save the Obsidian note (filename is auto-generated as YYYY-MM-DD-HH-MM-SS-video-clip.md)",
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded audio file",
    )

    args = parser.parse_args()

    try:
        # Generate timestamp for consistent filename
        timestamp = datetime.now()

        # Detect platform
        print(f"Detecting platform for: {args.url}")
        platform = detect_platform(args.url)
        print(f"Detected platform: {platform}")

        # Create temp directory for audio
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download video/audio
            print("Downloading video...")
            audio_path, metadata = download_video(args.url, temp_dir)
            print(f"Downloaded: {metadata.get('title', 'Unknown')}")

            # Transcribe
            transcript = transcribe_audio(audio_path, args.model)
            print(f"Transcription complete ({len(transcript)} characters)")

            # Generate summary
            summary = generate_summary(transcript)

            # Create note
            note_path = create_obsidian_note(
                url=args.url,
                platform=platform,
                metadata=metadata,
                transcript=transcript,
                summary=summary,
                output_dir=args.output_path,
                timestamp=timestamp,
            )
            print(f"Note saved to: {note_path}")

            # Optionally keep audio
            if args.keep_audio:
                audio_filename = timestamp.strftime("%Y-%m-%d-%H-%M-%S-video-clip.mp3")
                audio_dest = Path(args.output_path) / audio_filename
                shutil.copy(audio_path, audio_dest)
                print(f"Audio saved to: {audio_dest}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
