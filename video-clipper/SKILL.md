# video-clipper

Download and transcribe videos from TikTok, YouTube, or Instagram Reels, creating an Obsidian note with metadata and transcript.

## Usage

```
/video-clipper <url> <output_directory>
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `url` | Yes | URL of the video (YouTube, TikTok, or Instagram Reel) |
| `output_directory` | Yes | Directory to save the Obsidian note |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--model` | `base` | Whisper model size: `tiny`, `base`, `small`, `medium`, `large` |
| `--keep-audio` | `false` | Keep the downloaded audio file alongside the note |

## Output

Creates an Obsidian markdown note with:
- YAML frontmatter (title, platform, creator, upload date, duration, source URL, tags)
- Clickable link to original video
- 1-2 sentence summary
- Full transcript

Filename format: `YYYY-MM-DD-HH-MM-SS-video-clip.md`

## Supported Platforms

- YouTube (`youtube.com`, `youtu.be`, YouTube Shorts)
- TikTok (`tiktok.com`)
- Instagram Reels (`instagram.com/reel/...`)

## Examples

```bash
# Transcribe a YouTube video
/video-clipper "https://youtube.com/watch?v=xxx" ~/Obsidian/Clips/

# Transcribe a TikTok with larger model for better accuracy
/video-clipper "https://tiktok.com/@user/video/123" ~/Obsidian/Clips/ --model medium

# Keep the audio file
/video-clipper "https://instagram.com/reel/xxx" ~/Obsidian/Clips/ --keep-audio
```

## Requirements

- Python 3.10+
- ffmpeg (for audio extraction)
- Virtual environment with dependencies (auto-configured in `venv/`)
