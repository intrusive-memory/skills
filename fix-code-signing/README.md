# Fix Code Signing Skill

**Category:** Build & CI/CD
**Platforms:** macOS, iOS (affects macOS test execution)
**Complexity:** Medium

## Description

Automatically diagnoses and fixes code signing configuration issues for XCTest bundles that fail to load into hardened runtime macOS applications.

## When to Use

Invoke this skill when you encounter:

- `Command CodeSign failed with a nonzero exit code` in Xcode Cloud
- Test bundle loading failures on macOS
- "Bundle couldn't be loaded" errors for test targets
- Dynamic loader rejecting unsigned test bundles

## Usage

```bash
/fix-code-signing
```

Or via Claude:
```
"Fix the code signing issues for my test targets"
"My tests are failing with CodeSign errors"
"Run the fix-code-signing skill"
```

## What It Does

1. **Diagnoses** - Scans project.pbxproj for incorrect test target signing settings
2. **Reports** - Shows current configuration and identifies problems
3. **Fixes** - Corrects CODE_SIGN_STYLE, removes disabling flags, ensures proper team
4. **Verifies** - Confirms changes were applied correctly
5. **Commits** - Creates descriptive commit with fix details

## Prerequisites

- Project must be in a git repository
- Must have write access to project.pbxproj
- Development team ID must be configured (H3EJ6Y8VJ6 for Produciesta)

## Common Scenarios

### Scenario 1: Xcode Cloud Failing
**Symptom:** Build succeeds locally but fails on Xcode Cloud with "CodeSign failed"
**Cause:** Test targets have CODE_SIGNING_ALLOWED = NO
**Fix:** Skill restores automatic signing for test bundles

### Scenario 2: Local macOS Tests Fail
**Symptom:** Tests run on iOS simulator but fail on macOS
**Cause:** Main app has hardened runtime, test bundles are unsigned
**Fix:** Skill enables automatic signing while keeping hardened runtime disabled

### Scenario 3: After Xcode Upgrade
**Symptom:** Tests worked before, now failing after Xcode update
**Cause:** Xcode migration changed signing settings
**Fix:** Skill resets to correct configuration

## Technical Details

### Test Target Requirements
When main app has `ENABLE_HARDENED_RUNTIME = YES`:
- Test bundles MUST be signed (automatic or manual)
- Test bundles should NOT have hardened runtime (ENABLE_HARDENED_RUNTIME = NO)
- Test bundles should NOT be sandboxed (ENABLE_APP_SANDBOX = NO)

### Configuration IDs
The skill operates on these test target configurations:
- `D6075FCD2EA6F42E006C02A6` - ProduciestaTests Debug
- `D6075FCE2EA6F42E006C02A6` - ProduciestaTests Release
- `D6075FD02EA6F42E006C02A6` - ProduciestaUITests Debug
- `D6075FD12EA6F42E006C02A6` - ProduciestaUITests Release

## Safety

✅ **Safe to run multiple times** - Idempotent, won't break working configuration
✅ **Git required** - Changes can be reverted if needed
✅ **User confirmation** - Asks before making changes
✅ **Verification step** - Confirms settings are correct after changes

## Output

The skill provides:
- Current configuration analysis
- List of problems found
- Changes to be made
- Verification results
- Git commit hash for reference

## Related Skills

- `/build` - Build project after fixing code signing
- `/test` - Run tests to verify fix works
- `/commit` - Commit additional related changes

## Version History

- **v1.0.0** (2024-12-25) - Initial creation based on Xcode Cloud build #370-372 failures

## Author

Created for Produciesta project after diagnosing hardened runtime test bundle signing requirements.
