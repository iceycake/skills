# Raindrop.io Bookmark Manager

Manage Andy's Raindrop.io bookmarks — save links, search, organize with tags/collections, and attach notes.

## Setup

Requires `RAINDROP_TOKEN` environment variable set to a Raindrop.io test token.
Generate at: https://app.raindrop.io/settings/integrations → create app → "Create test token"

## Commands

### Save a bookmark
```bash
raindrop create "https://example.com" --tags "python,tutorial" --parse
```
The `--parse` flag lets Raindrop auto-fill title and excerpt from the page.

Add a note inline:
```bash
raindrop create "https://example.com" --note "Great intro to async patterns" --parse
```

Add a long note from a file (e.g. a transcription):
```bash
raindrop create "https://example.com" --note-file /path/to/transcript.txt --parse
```

Pipe content as a note:
```bash
cat transcript.txt | raindrop create "https://example.com" --note - --parse
```

### Search bookmarks
```bash
raindrop search "machine learning"
raindrop search "python" --collection 12345
raindrop search "react" --sort -created   # newest first
```

### List bookmarks
```bash
raindrop list                    # all bookmarks
raindrop list 12345              # bookmarks in collection 12345
raindrop list --sort -created --perpage 10
```

### Get a single bookmark
```bash
raindrop get 123456
```

### Update a bookmark
```bash
raindrop update 123456 --tags "python,advanced" --title "New Title"
raindrop update 123456 --note "Updated note"
raindrop update 123456 --note-file /path/to/notes.txt
raindrop update 123456 --important    # mark as favorite
raindrop update 123456 --collection 12345
```

### Delete a bookmark
```bash
raindrop delete 123456
```
Moves to trash (recoverable in Raindrop.io).

### Collections
```bash
raindrop collections
```

### Tags
```bash
raindrop tags                        # all tags
raindrop tags --collection 12345     # tags in collection
raindrop tag-rename "oldname" "newname"
raindrop tag-delete "obsolete" "typo"
```

## Output

All commands output JSON by default. Add `--pretty` for human-readable formatting.

Errors go to stderr with a non-zero exit code.

## Common Workflows

**Save a link from Telegram with tags:**
```bash
raindrop create "https://..." --tags "fromtelegram,ai" --parse
```

**Transcribe a video then save with transcript as note:**
```bash
# 1. Transcribe
python3 /home/clawuser/.openclaw/workspace/skills/video-clipper/video_clipper.py "https://youtube.com/..." /tmp
# 2. Save bookmark with transcription file as note
raindrop create "https://youtube.com/..." --note-file /path/to/transcript.txt --tags "video,transcript" --parse
```

**Find and organize bookmarks:**
```bash
raindrop search "python tutorial"
raindrop update 123456 --collection 12345 --tags "python,learning"
```

**Clean up tags:**
```bash
raindrop tags
raindrop tag-rename "ml" "machine-learning"
raindrop tag-delete "temp" "misc"
```
