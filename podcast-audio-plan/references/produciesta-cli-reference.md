# Produciesta CLI Reference

Complete reference for the Produciesta command-line tool.

## Installation & Build

```bash
# Navigate to Produciesta project
cd ~/Projects/Produciesta

# Build CLI (if needed)
swift build -c release

# Binary location
# ~/Projects/Produciesta/.build/release/produciesta
```

## Basic Usage

```bash
# Generate audio for entire project (with existing cast list)
produciesta /path/to/project

# First-time setup with auto-casting
produciesta /path/to/project --autocast --provider apple

# Preview without generating
produciesta /path/to/project --dry-run

# Single episode
produciesta /path/to/project --episode chapter-01.fountain

# Direct file path
produciesta /path/to/project/episodes/chapter-01.fountain
```

## Voice Providers

### Apple Neural TTS (Free)

**No setup required** - works out of the box on macOS.

```bash
# List available voices
say -v '?'

# Generate with Apple voices
produciesta /path/to/project --provider apple
```

**Voice URI format:**
```
apple://com.apple.voice.premium.en-US.Aaron
```

**Popular voices:**
- Aaron (US male)
- Ava (US female)
- Daniel (UK male)
- Samantha (US female)
- Fred (US male, novelty)

### ElevenLabs (Paid)

**Requires API key:**

```bash
# Set API key
export ELEVENLABS_API_KEY="your-key-here"

# Generate with ElevenLabs voices
produciesta /path/to/project --provider elevenlabs
```

**Voice URI format:**
```
elevenlabs://21m00Tcm4TlvDq8ikWAM
```

**Popular voices:**
- `21m00Tcm4TlvDq8ikWAM` - Rachel (US female)
- `EXAVITQu4vr4xnSDxMaL` - Bella (US female)
- `pNInz6obpgDQGcFmaJgB` - Adam (US male)

## Command-Line Flags

### Required Arguments

| Argument | Description |
|----------|-------------|
| `projectPath` | Path to screenplay file or project directory |

### Output Options

| Flag | Description | Example |
|------|-------------|---------|
| `-o, --output <path>` | Override output directory | `--output /custom/path` |
| `-e, --episode <name>` | Generate single episode only | `--episode pilot.fountain` |
| `-f, --format <format>` | Audio format (m4a, aiff, wav, caf, mp3) | `--format m4a` |

### Processing Options

| Flag | Description |
|------|-------------|
| `--skip-existing` | Skip files that already have audio |
| `--resume-from <N>` | Resume from file number N |
| `--regenerate` | Force regenerate all audio |
| `--skip-hooks` | Skip pre/post generation hooks |
| `--fail-fast` | Stop on first error |
| `--ignore-generation-errors` | Continue on voice resolution errors |

### Display Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Show plan without generating |
| `--verbose` | Enable detailed logging |
| `--quiet` | Suppress output (errors only) |
| `--json` | JSON output for CI/CD |

### Voice Options

| Flag | Description | Example |
|------|-------------|---------|
| `--default-voice <uri>` | Voice for unassigned characters | `--default-voice "apple://..."` |
| `--no-cast-list` | Ignore cast list, use default voice | `--no-cast-list --default-voice "..."` |

### AUTO-CAST Options (Phase 0)

| Flag | Description |
|------|-------------|
| `--autocast` | Enable LLM-based character extraction and voice matching |
| `--provider <provider>` | Voice provider (apple, elevenlabs) |
| `--no-cast-extraction` | Skip character extraction (use existing cast) |
| `--no-voice-matching` | Skip voice matching (extract characters only) |
| `--force-regenerate` | Force regenerate cast and voices in PROJECT.md |

### Help

| Flag | Description |
|------|-------------|
| `--help-examples` | Show comprehensive usage examples |
| `--version` | Show version |

## Workflow Phases

### Phase 0: PROJECT.md Regeneration

**Always runs before audio generation.**

```bash
# Default behavior: Validate episode count only
produciesta /path/to/project

# With --autocast: Extract characters and match voices
produciesta /path/to/project --autocast --provider apple
```

**What happens:**
1. Validates or creates PROJECT.md
2. Updates episode count if changed
3. With `--autocast`:
   - Extracts character list from .fountain files (LLM)
   - Matches voices to characters for specified provider (LLM)
   - Updates cast section in PROJECT.md

### Phases 1-6: Audio Generation

1. **Validation** - Environment, PROJECT.md, file discovery
2. **Parsing** - Parse Fountain screenplay format
3. **Voice Resolution** - Map characters to TTS providers
4. **Generation** - Synthesize audio for each element
5. **Export** - Concatenate and export audio files
6. **Hooks** - Run pre/post-processing scripts (macOS only)

## Auto-Cast Workflows

### Full Auto-Cast (First Time)

Extract characters and assign voices:

```bash
# Apple voices
produciesta /path/to/project --autocast --provider apple

# ElevenLabs voices
export ELEVENLABS_API_KEY="your-key-here"
produciesta /path/to/project --autocast --provider elevenlabs
```

### Extract Characters Only

Extract character list without assigning voices:

```bash
produciesta /path/to/project \
  --autocast \
  --no-voice-matching
```

Use case: Manual voice assignment after character extraction

### Match Voices Only

Assign voices to existing character list:

```bash
produciesta /path/to/project \
  --autocast \
  --no-cast-extraction \
  --provider apple
```

Use case: Re-assign voices after manual character list creation

### Force Re-Cast

Overwrite existing cast list:

```bash
produciesta /path/to/project \
  --force-regenerate \
  --autocast \
  --provider elevenlabs
```

Use case: Switch providers or update voice assignments

## Batch Processing

### Resume Interrupted Generation

```bash
# Resume from episode 100
produciesta /path/to/project --resume-from 100

# Resume with skip-existing
produciesta /path/to/project --skip-existing
```

### Large Projects

```bash
# TV series with 100+ episodes
produciesta /path/to/series \
  --format m4a \
  --skip-existing \
  --verbose \
  > generation.log 2>&1
```

## Hooks (macOS Only)

### Create Hooks

```bash
mkdir -p /path/to/project/.produciesta-hooks

# Pre-generation hook
cat > /path/to/project/.produciesta-hooks/pre-generation.sh << 'EOF'
#!/bin/bash
echo "Starting generation at $(date)"
# Validation, setup, notifications
EOF

# Post-generation hook
cat > /path/to/project/.produciesta-hooks/post-generation.sh << 'EOF'
#!/bin/bash
echo "Completed generation at $(date)"
# Upload to R2, update RSS, deploy
EOF

chmod +x /path/to/project/.produciesta-hooks/*.sh
```

### Disable Hooks

```bash
produciesta /path/to/project --skip-hooks
```

## Error Handling

### Error Log

All errors are written to: `GENERATION_ERRORS.md` in project root.

```bash
# View errors
cat /path/to/project/GENERATION_ERRORS.md
```

### Continue on Error (Default)

Batch processing continues after errors:

```bash
produciesta /path/to/project
# Errors logged to GENERATION_ERRORS.md
# Processing continues
```

### Stop on First Error

```bash
produciesta /path/to/project --fail-fast
# Exits immediately on error
```

## CI/CD Integration

### JSON Output Mode

```bash
produciesta /path/to/project \
  --quiet \
  --json \
  --fail-fast \
  > generation-log.jsonl

# Parse with jq
cat generation-log.jsonl | jq -r 'select(.event == "episode_complete")'
```

### Event Types

- `episode_started`
- `parsing_complete`
- `element_progress`
- `export_started`
- `episode_complete`
- `generation_complete`

## Output Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| `m4a` | `.m4a` | Apple AAC (recommended, smallest) |
| `aiff` | `.aiff` | Uncompressed (best quality, large) |
| `wav` | `.wav` | Standard PCM (widely compatible) |
| `caf` | `.caf` | Core Audio Format (macOS native) |
| `mp3` | `.mp3` | MPEG Layer 3 (universal) |

## Examples

### Quick Start (New Project)

```bash
cd ~/my-podcast
produciesta . --autocast --provider apple --format m4a
```

### Generate with Existing Cast

```bash
produciesta ~/my-podcast
```

### Single Episode Test

```bash
produciesta ~/my-podcast --episode pilot.fountain --verbose
```

### Batch with Resume

```bash
produciesta ~/my-podcast --skip-existing --resume-from 50
```

### Switch to ElevenLabs

```bash
export ELEVENLABS_API_KEY="your-key"
produciesta ~/my-podcast \
  --force-regenerate \
  --autocast \
  --provider elevenlabs \
  --regenerate
```

### Dry Run

```bash
produciesta ~/my-podcast --dry-run --autocast --provider apple
```

## PROJECT.md Structure

Produciesta auto-generates and validates PROJECT.md:

```yaml
---
type: project
title: My Podcast
author: Author Name
description: Podcast description
episodesDir: episodes
audioDir: audio
filePattern: "*.fountain"
exportFormat: m4a
cast:
  - character: NARRATOR
    voices:
      - apple://com.apple.voice.premium.en-US.Aaron
  - character: ALICE
    voices:
      - apple://com.apple.voice.premium.en-US.Ava
---

## Production Notes
Optional markdown content for documentation.
```

## Troubleshooting

### Voice Provider Issues

**ElevenLabs API key not set:**
```bash
export ELEVENLABS_API_KEY="your-key-here"
```

**Apple voice not available:**
- Download premium voices: System Settings → Accessibility → Spoken Content

### File Discovery Issues

**No episodes found:**
```bash
# Check file pattern
produciesta /path/to/project --dry-run

# Update filePattern in PROJECT.md
```

**Episode not discovered:**
```bash
# List files in episodes directory
ls -la /path/to/project/episodes/*.fountain
```

### Character Casting Issues

**Character not in cast list:**

Option 1: Auto-cast
```bash
produciesta /path/to/project --autocast --provider apple
```

Option 2: Manual addition to PROJECT.md
```yaml
cast:
  - character: NEW_CHARACTER
    voices:
      - apple://com.apple.voice.premium.en-US.Aaron
```

Option 3: Default voice
```bash
produciesta /path/to/project \
  --default-voice "apple://com.apple.voice.premium.en-US.Aaron"
```

### Performance Issues

**Slow generation:**
- Use `--skip-existing` for incremental updates
- Use M4A format (faster than AIFF/WAV)
- Check network latency for ElevenLabs

**Out of memory:**
- Process episodes individually with `--episode`
- Use `--resume-from` to batch in chunks

## Best Practices

1. **Always use `--dry-run` first** to validate configuration
2. **Commit PROJECT.md** to version control for team collaboration
3. **Test with one episode** before batch processing
4. **Use `--skip-existing`** for incremental updates
5. **Enable `--verbose`** when debugging
6. **Use hooks** for automation (deployment, RSS updates)
7. **Set reasonable timeouts** for ElevenLabs API calls
8. **Back up generated audio** before regenerating

## Related Documentation

- [Produciesta README](~/Projects/Produciesta/README.md)
- [ProduciestaCore Documentation](~/Projects/Produciesta/ProduciestaCore/)
- [Fountain Format Specification](https://fountain.io/)
- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
