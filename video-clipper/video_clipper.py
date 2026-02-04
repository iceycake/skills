"""
Video Clipper - Download and transcribe videos from TikTok, YouTube, or Instagram Reels.
Creates an Obsidian note with metadata, summary, and full transcript.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


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
    output_template = os.path.join(output_dir, "%(id)s.%(ext)s")

    # Use yt-dlp CLI to download and extract audio
    cmd = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "mp3",
        "--audio-quality", "192K",
        "-o", output_template,
        "--print-json",  # Output JSON metadata
        "--no-warnings",
        "--quiet",
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr or result.stdout}")

    # Parse JSON output to get metadata
    info = json.loads(result.stdout)
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
    """Transcribe audio file using whisper-cli."""
    # Find model path - check common locations
    model_file = f"ggml-{model_name}.bin"
    model_paths = [
        Path.home() / ".cache" / "whisper-cpp" / model_file,
        Path.home() / ".local" / "share" / "whisper-cpp" / model_file,
        Path("/usr/local/share/whisper-cpp") / model_file,
        Path("/opt/homebrew/share/whisper-cpp") / model_file,
    ]

    model_path = None
    for path in model_paths:
        if path.exists():
            model_path = path
            break

    if not model_path:
        raise FileNotFoundError(
            f"Whisper model '{model_name}' not found. Please download it:\n"
            f"  curl -L -o ~/.cache/whisper-cpp/{model_file} "
            f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{model_file}"
        )

    print(f"Transcribing audio with whisper-cli (model: {model_name})...")

    # Output file path (without extension, whisper-cli adds .txt)
    output_base = audio_path.rsplit(".", 1)[0]

    cmd = [
        "whisper-cli",
        "-m", str(model_path),
        "-f", audio_path,
        "--no-timestamps",
        "--output-txt",
        "--output-file", output_base,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"whisper-cli failed: {result.stderr or result.stdout}")

    # Read the output text file
    txt_path = output_base + ".txt"
    if os.path.exists(txt_path):
        with open(txt_path, "r") as f:
            transcript = f.read().strip()
        os.remove(txt_path)  # cleanup
    else:
        # Fallback to stdout if no file created
        transcript = result.stdout.strip()

    return transcript


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
