# Instructions for Podcast Validation Skill

When this skill is invoked, follow these steps:

## 1. Parse User Input

Determine what validation to run:
- `cdn` or `cdn <url>` - Validate CDN audio links only
- `site` or `site <url>` - Validate site links only
- `all` or `all <cdn_url> <site_url>` - Validate both

Default URLs:
- CDN: `https://pub-8e049ed02be340cbb18f921765fd24f3.r2.dev`
- Site: `http://127.0.0.1:4000` (local Jekyll)

## 2. Change to Project Directory

```bash
cd /Users/stovak/Projects/intrusive-memory.github.com
```

## 3. Run Validation

### For CDN Validation:
```bash
./scripts/validate-cdn-links.sh [cdn_url]
```

### For Site Validation:
```bash
./scripts/validate-site-links.sh [site_url]
```

### For Both:
Run both scripts sequentially.

## 4. Present Results

After running the script(s):

1. **Show the terminal output** - The scripts provide color-coded output
2. **Read the JSON results** - Parse `.cdn-validation-results.json` and/or `.site-validation-results.json`
3. **Summarize findings**:
   - Which podcasts are fully validated (all ✓)
   - Which podcasts have missing audio
   - Any broken site links
   - Overall pass/fail status

4. **Provide recommendations**:
   - If CDN files are missing: "Audio needs to be uploaded to CDN for: [list]"
   - If using Cloudflare alias and getting 404s: "Cloudflare alias may not have propagated yet. Wait 24-48 hours."
   - If all pass: "All validations passed! Site is ready for deployment."

## 5. Exit Codes

- Exit code 0: All validations passed
- Exit code 1: Some validations failed

Use exit codes to determine overall success/failure.

## Important Notes

- **Never display environment variables or secrets**
- Scripts use environment variables internally but don't echo them
- JSON results files are excluded from git (in .gitignore)
- Scripts are designed to be CI/CD friendly
- Validation can run against local (Jekyll serve) or production URLs

## Examples

### Example 1: Validate CDN with default R2 URL
```
User: /podcast-validate cdn
```
Run: `./scripts/validate-cdn-links.sh`

### Example 2: Validate CDN with Cloudflare alias
```
User: /podcast-validate cdn https://audio.intrusive-memory.productions
```
Run: `./scripts/validate-cdn-links.sh https://audio.intrusive-memory.productions`

### Example 3: Validate local site
```
User: /podcast-validate site
```
Run: `./scripts/validate-site-links.sh http://127.0.0.1:4000`

### Example 4: Full production validation
```
User: /podcast-validate all https://audio.intrusive-memory.productions https://intrusive-memory.productions
```
Run both scripts with production URLs.

## Success Criteria

A successful validation means:
- All published podcasts (Daily Dao, Meditations, Mr & Mr Charles) show 100% ✓
- All site pages return HTTP 200
- All RSS feeds are accessible
- No broken links detected

In-progress podcasts (YNTSWYD, Lazarillo, etc.) may show missing audio - this is expected until audio is uploaded.
