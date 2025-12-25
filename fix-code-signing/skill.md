# Fix Code Signing for Test Targets

Diagnoses and fixes code signing configuration issues for XCTest bundles that fail to load into hardened runtime macOS apps.

## Common Symptoms

This skill addresses the following error patterns:

### 1. Xcode Cloud Build Failures
```
Command CodeSign failed with a nonzero exit code
```
- Occurs during TEST phase
- Build succeeds but tests fail to run
- Error message may mention "signature" or "validation"

### 2. Local Test Failures
```
The bundle "<YourApp>Tests" couldn't be loaded because it is damaged or missing necessary resources.
```
- Tests fail immediately on launch
- May see "Code signature invalid" in Console.app
- Occurs on macOS only (iOS simulator tests may work fine)

### 3. Dynamic Loader Errors
```
dyld: Library not loaded: @rpath/XCTest.framework/XCTest
Reason: no suitable image found
```
- macOS security validation rejecting unsigned test bundles
- Hardened runtime host requires all loaded bundles to be signed
- Test bundles are loaded dynamically at runtime

## Root Cause

**The Problem:**
- Main app has `ENABLE_HARDENED_RUNTIME = YES` (required for App Store distribution)
- macOS hardened runtime validates signatures of ALL loaded bundles at runtime
- Test bundles (.xctest) are dynamically loaded into the app process during testing
- If test bundles are unsigned (CODE_SIGNING_ALLOWED = NO), the dynamic loader rejects them

**Why This Happens:**
Developers sometimes disable code signing on test targets to avoid certificate issues or speed up builds. However, when the main app has hardened runtime enabled, this creates a security validation mismatch.

## Diagnostic Steps

The skill will check the following in `<YourApp>.xcodeproj/project.pbxproj`:

### 1. Main App Configuration
Look for main app target build settings:
```
ENABLE_HARDENED_RUNTIME = YES;  // Main app needs this for App Store
```

### 2. Test Target Configuration Issues
Search for `<YourApp>Tests` and `<YourApp>UITests` configurations and identify:

**Red Flags (Incorrect):**
```
CODE_SIGNING_ALLOWED = NO;          // ❌ Prevents signing
CODE_SIGNING_REQUIRED = NO;         // ❌ Prevents signing
CODE_SIGN_IDENTITY = "-";           // ❌ Disables signing
CODE_SIGN_STYLE = Manual;           // ❌ (unless you have specific certs)
```

**Correct Settings:**
```
CODE_SIGN_STYLE = Automatic;        // ✅ Auto-sign test bundles
DEVELOPMENT_TEAM = <YOUR_TEAM_ID>;  // ✅ Team for signing
ENABLE_HARDENED_RUNTIME = NO;       // ✅ Tests don't need hardening
ENABLE_APP_SANDBOX = NO;            // ✅ Tests need broader access
// No CODE_SIGNING_ALLOWED setting    ✅ Defaults to YES
// No CODE_SIGNING_REQUIRED setting   ✅ Defaults to YES
// No CODE_SIGN_IDENTITY = "-"        ✅ Auto-selected by Xcode
```

## Resolution Process

### Step 1: Identify Affected Configurations
Find all test target configurations:
- `<YourApp>Tests` Debug
- `<YourApp>Tests` Release
- `<YourApp>UITests` Debug
- `<YourApp>UITests` Release

### Step 2: Fix Each Configuration
For each configuration, apply these changes:

**Remove These Settings (if present):**
```
CODE_SIGNING_ALLOWED = NO;
CODE_SIGNING_REQUIRED = NO;
CODE_SIGN_IDENTITY = "-";
```

**Set or Verify These Settings:**
```
CODE_SIGN_STYLE = Automatic;
DEVELOPMENT_TEAM = <YOUR_TEAM_ID>;
ENABLE_HARDENED_RUNTIME = NO;
ENABLE_APP_SANDBOX = NO;
```

### Step 3: Search and Replace Pattern

Use grep to find test target configuration blocks in your project.pbxproj:
```bash
grep -n "<YourApp>Tests\|<YourApp>UITests" project.pbxproj
```

Each configuration has a unique ID (e.g., `D6075FCD2EA6F42E006C02A6`). Find the IDs for your test targets by searching for their names in the project file.

### Step 4: Verify the Fix

After making changes:

1. **Read the updated sections** to confirm correct settings
2. **Build both test targets:**
   ```bash
   xcodebuild build-for-testing -scheme <YourApp> \
     -destination 'platform=macOS,arch=arm64'
   ```
3. **Run tests locally:**
   ```bash
   xcodebuild test -scheme <YourApp> \
     -destination 'platform=macOS,arch=arm64'
   ```
4. **Check code signing:**
   ```bash
   codesign -dv ~/Library/Developer/Xcode/DerivedData/.../<YourApp>Tests.xctest
   ```
   Should show: "Signature=adhoc" or valid developer signature

## Implementation

When this skill is invoked:

1. **Read** `<YourApp>.xcodeproj/project.pbxproj`
2. **Search** for test target configuration blocks
3. **Identify** incorrect settings (CODE_SIGNING_ALLOWED=NO, etc.)
4. **Report** findings to user with line numbers
5. **Ask** user for confirmation to proceed with fixes
6. **Edit** project.pbxproj to apply correct settings
7. **Verify** changes were applied correctly
8. **Commit** with descriptive message
9. **Recommend** running tests to verify fix

## Expected Outcome

After running this skill:

✅ Test bundles will be automatically signed
✅ Test bundles will load into hardened runtime app
✅ Xcode Cloud builds will pass
✅ Local tests will run successfully
✅ No "CodeSign failed" errors

## Related Documentation

- Apple Documentation: "Hardened Runtime" and "Code Signing Guide"
- Your project's CLAUDE.md or README.md may have project-specific notes
