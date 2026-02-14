# Podcast Validation Skill

Validates podcast CDN links and site integrity for intrusive-memory.productions.

## When to Use

Use this skill when:
- After uploading audio to CDN (R2 or Cloudflare alias)
- Before deploying/publishing podcast updates
- After DNS propagation (24+ hours after creating Cloudflare alias)
- When debugging broken podcast links
- As part of pre-deployment checks

## What This Skill Does

This skill performs comprehensive validation:

1. **CDN Audio Validation**
   - Tests all audio file URLs from episode data
   - Verifies HTTP 200 OK responses
   - Reports missing files by podcast
   - Supports both R2 direct URLs and Cloudflare aliases
   - Outputs JSON results for automation

2. **Site Link Validation**
   - Tests core pages (home, podcasts, projects)
   - Validates all podcast player pages
   - Checks RSS feed accessibility
   - Verifies internal navigation
   - Tests against local or production URLs

## Usage

### Basic CDN Validation (R2 Direct)
```
/podcast-validate cdn
```

### CDN Validation with Cloudflare Alias
```
/podcast-validate cdn https://audio.intrusive-memory.productions
```

### Site Link Validation (Local)
```
/podcast-validate site
```

### Site Link Validation (Production)
```
/podcast-validate site https://intrusive-memory.productions
```

### Full Validation (Both CDN and Site)
```
/podcast-validate all
```

### With Custom URLs
```
/podcast-validate all https://audio.intrusive-memory.productions https://intrusive-memory.productions
```

## Output

The skill provides:
- Color-coded terminal output (✓ green for OK, ✗ red for failed)
- Per-podcast summaries showing OK/failed counts
- Overall summary with total statistics
- JSON results files for automation:
  - `.cdn-validation-results.json` - CDN validation details
  - `.site-validation-results.json` - Site link validation details
- Exit code 0 for success, 1 for failures (CI/CD friendly)

## Integration with Workflows

### Pre-Deployment Check
```bash
# Validate before deploying
./scripts/validate-cdn-links.sh https://audio.intrusive-memory.productions && \
./scripts/validate-site-links.sh https://intrusive-memory.productions && \
echo "✓ Ready to deploy"
```

### Post-Upload Verification
```bash
# After uploading new podcast audio
./scripts/validate-cdn-links.sh
```

### CI/CD Pipeline
```yaml
- name: Validate Podcast Links
  run: |
    ./scripts/validate-cdn-links.sh
    ./scripts/validate-site-links.sh https://intrusive-memory.productions
```

## Expected Results

**Fully Published Podcasts** (should show all ✓):
- Daily Dao - 81 chapters
- Meditations - 365 episodes
- Mr & Mr Charles - 10 episodes

**In Progress Podcasts** (may show ✗ for missing audio):
- YNTSWYD - 9 episodes (audio pending)
- Lazarillo - 8 episodes (audio pending)
- Therapist GPT - 2 episodes (audio pending)
- Casting Software Spells - 12 episodes (audio pending)

## Troubleshooting

**All files showing as 404**:
- CDN URL may be incorrect
- Cloudflare alias may not have propagated (wait 24-48 hours)
- Audio files may not be uploaded yet

**Some files missing**:
- Check episode data in `_data/*_episodes.yml`
- Verify file names match exactly (case-sensitive)
- Confirm files exist in CDN at correct paths

**Connection timeouts (HTTP 000)**:
- Network connectivity issues
- CDN may be down
- URL may be invalid

## Scripts Location

- CDN validation: `/scripts/validate-cdn-links.sh`
- Site validation: `/scripts/validate-site-links.sh`

Both scripts are executable and can be run independently.
