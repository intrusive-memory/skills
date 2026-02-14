# Podcast Audio Plan Skill

Claude Code skill for generating podcast audio from Fountain screenplays using Produciesta CLI.

## Overview

This skill provides guidance for using **Claude-assisted voice casting** combined with the **Produciesta CLI** to generate professional podcast audio from Fountain screenplay files. Claude handles character analysis and voice assignment by writing directly to PROJECT.md, while Produciesta handles audio generation.

## What This Skill Does

- **Analyzes Fountain files** to extract character lists (Claude)
- **Matches characters to voices** intelligently based on traits (Claude)
- **Writes PROJECT.md** with proper YAML cast list (Claude)
- **Generates audio** using Produciesta CLI
- **Provides templates** for execution plans and project documentation
- **Documents best practices** for Fountain screenplay writing
- **Offers troubleshooting** guidance for common issues

## Key Changes from Previous Version

### Old Approach (Deprecated)
- Python scripts for parsing PROJECT.md and Fountain files
- Manual template substitution
- Separate tools for analysis and generation
- Required SwiftHablare, SwiftOnce coordination

### New Approach (Current)
- **Claude-assisted casting**: Analyzes characters, assigns voices, writes PROJECT.md
- **Single CLI tool**: Produciesta handles audio generation
- **No autocast needed**: Claude provides better control than Produciesta's autocast (currently not working)
- **Integrated pipeline**: Analysis by Claude, generation by Produciesta
- **ProduciestaCore**: All audio dependencies bundled

## Files

```
podcast-audio-plan/
├── SKILL.md                                    # Main skill definition
├── README.md                                   # This file
└── references/
    ├── produciesta-cli-reference.md           # Complete CLI documentation
    └── fountain-format-guide.md               # Fountain syntax for podcasts
```

## Usage

When invoked by Claude Code, this skill:

1. **Analyzes project structure** to understand requirements
2. **Recommends Produciesta commands** for the user's specific situation
3. **Generates execution plans** with step-by-step instructions
4. **Documents workflows** for team collaboration
5. **Troubleshoots issues** with voice assignment, file discovery, etc.

## Typical Workflows

### First-Time Project Setup

**Step 1: Claude analyzes and creates PROJECT.md**
1. User asks: "Cast voices for my podcast project"
2. Claude reads Fountain files from `episodes/`
3. Claude queries available voices (`say -v '?'` or ElevenLabs MCP)
4. Claude writes PROJECT.md with cast list

**Step 2: Generate audio**
```bash
# Generate audio using Claude's cast list
produciesta /path/to/podcast --format m4a --verbose
```

### Generate with Existing Cast

```bash
# Use existing PROJECT.md cast list
produciesta /path/to/podcast --format m4a
```

### Preview Before Generating

```bash
# Dry run to validate configuration
produciesta /path/to/podcast --dry-run
```

## Requirements

- **Produciesta CLI** at `~/Projects/Produciesta/produciesta-cli/`
- **Swift 6.2+** (for building Produciesta)
- **Xcode 16+** (macOS)
- **PROJECT.md** with YAML front matter (auto-generated if missing)
- **Fountain files** in standard format

## Voice Providers

### Apple Neural TTS (Free)
- No API key required
- Premium voices included with macOS
- Best for English podcasts

### ElevenLabs (Paid)
- Requires `ELEVENLABS_API_KEY` environment variable
- High-quality, natural voices
- Best for professional production

## Key Features

### Claude-Assisted Casting
Intelligent character analysis and voice matching:
- Claude reads Fountain files
- Analyzes character traits from dialogue
- Queries available voices
- Writes PROJECT.md with cast list

### Batch Processing
Handle large projects with resume capability:

```bash
produciesta . --skip-existing --resume-from 50
```

### Hooks (macOS Only)
Pre/post-generation automation:

```bash
.produciesta-hooks/
├── pre-generation.sh    # Validation, setup
└── post-generation.sh   # Upload, RSS update, deploy
```

### Error Handling
Errors logged to `GENERATION_ERRORS.md` for review

### CI/CD Integration
JSON output mode for automated builds:

```bash
produciesta . --quiet --json --fail-fast > log.jsonl
```

## Documentation

- **[SKILL.md](./SKILL.md)** - Main skill documentation with workflows
- **[Produciesta CLI Reference](./references/produciesta-cli-reference.md)** - Complete CLI documentation
- **[Fountain Format Guide](./references/fountain-format-guide.md)** - Screenplay syntax for podcasts

## Related Projects

- **[Produciesta](~/Projects/Produciesta)** - Main CLI tool and audio generation engine
- **[ProduciestaCore](~/Projects/Produciesta/ProduciestaCore)** - Audio generation library
- **[SwiftCompartido](~/Projects/SwiftCompartido)** - Shared utilities
- **[SwiftBruja](~/Projects/SwiftBruja)** - LLM query interface

## Migration from Old Skill

If you were using the old Python-based workflow:

1. **Remove Python scripts** - No longer needed
2. **Use Claude for casting** - Ask Claude to analyze and create PROJECT.md cast list
3. **Update PROJECT.md** - Use new voice URI format (see below)
4. **Use Produciesta CLI** - For audio generation only (not casting)

### Old Voice URI Format (Don't Use)
```
hablare://provider/voiceId?lang=en
```

### New Voice URI Format (Current)
```
apple://com.apple.voice.premium.en-US.Aaron
elevenlabs://21m00Tcm4TlvDq8ikWAM
```

## Contributing

This skill is maintained as part of the podcast-collection project. Updates should:

1. Keep documentation in sync with Produciesta CLI capabilities
2. Provide clear, concise examples
3. Include troubleshooting guidance
4. Reference current Produciesta version

## Version History

- **v2.0** (2026-02-11) - Rewritten to use Produciesta CLI
  - Removed Python scripts
  - Updated to use ProduciestaCore
  - Added autocast documentation
  - Simplified workflow
  - Updated voice URI format

- **v1.0** (2024) - Original Python-based skill
  - Manual PROJECT.md parsing
  - Separate SwiftHablare/SwiftOnce coordination
  - Template-based plan generation

## License

Part of the Intrusive Memory Productions podcast collection.
