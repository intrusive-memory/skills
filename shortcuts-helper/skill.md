# Shortcuts Helper Skill

## Purpose

Help users create, run, and understand macOS Shortcuts workflows that integrate with their applications. This skill provides guidance on using the Shortcuts CLI, URL schemes, and App Intents integration.

## Capabilities

1. **Generate Shortcuts CLI Commands**: Create shell scripts using the `shortcuts` command-line tool
2. **URL Scheme Generation**: Build `shortcuts://` URLs for triggering shortcuts from other apps
3. **Workflow Documentation**: Help users understand how to chain App Intents together in Shortcuts app
4. **Debugging & Testing**: Generate commands to list, run, and inspect shortcuts

## When to Use This Skill

- User wants to automate Shortcuts execution from Terminal or scripts
- User needs to integrate Shortcuts with other applications via URL schemes
- User wants examples of how to use app-specific App Intents in Shortcuts
- User needs to debug or test shortcut workflows programmatically

## Key Concepts

### Shortcuts Storage
- **macOS Location**: `~/Library/Mobile Documents/com~apple~CloudDocs/Shortcuts/`
- **iCloud Sync**: Shortcuts automatically sync across devices via iCloud
- **File Format**: `.shortcut` files are signed binary plists (not directly editable)

### Shortcuts CLI (macOS)

The `shortcuts` command-line tool allows running and managing shortcuts from Terminal:

```bash
# List all available shortcuts
shortcuts list

# Run a shortcut by name
shortcuts run "Shortcut Name"

# Run with input
shortcuts run "Shortcut Name" -i "input text"
shortcuts run "Shortcut Name" --input-path /path/to/file

# View help
shortcuts --help
shortcuts run --help
```

### URL Schemes

Shortcuts can be triggered via URL schemes from browsers, other apps, or AppleScript:

**Basic Execution:**
```
shortcuts://run-shortcut?name=MyShortcut
shortcuts://run-shortcut?name=MyShortcut&input=text&text=Hello
```

**With Callbacks (x-callback-url):**
```
shortcuts://x-callback-url/run-shortcut?name=MyShortcut&x-success=myapp://success&x-error=myapp://error
```

**Other Actions:**
```
shortcuts://open-shortcut?name=MyShortcut  # Open for editing
shortcuts://create-shortcut                 # Create new shortcut
shortcuts://import-shortcut?url=https://...  # Import from URL
```

### App Intents Integration

Modern apps expose actions to Shortcuts via the `AppIntent` protocol. Users build workflows by:
1. Opening Shortcuts app
2. Adding app-specific actions
3. Connecting actions with inputs/outputs
4. Running the workflow

This is the recommended approach for app developers (no file manipulation needed).

## Task Patterns

### Pattern 1: Generate CLI Script for Batch Processing

When user wants to run a shortcut on multiple files or in a loop:

```bash
#!/bin/bash
# Batch process files with a shortcut

for file in ~/Documents/*.pdf; do
    echo "Processing: $file"
    shortcuts run "Convert PDF" --input-path "$file"
done
```

### Pattern 2: Generate URL Scheme for App Integration

When user wants to trigger a shortcut from their app:

```swift
// Swift example
let shortcutName = "Process Screenplay"
let encodedName = shortcutName.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!
let url = URL(string: "shortcuts://run-shortcut?name=\(encodedName)")!
NSWorkspace.shared.open(url)
```

### Pattern 3: Generate x-callback-url with Error Handling

When user needs callbacks and error handling:

```
shortcuts://x-callback-url/run-shortcut?name=Export%20Audio&input=text&text=/path/to/file&x-success=myapp://export-complete&x-error=myapp://export-failed&x-cancel=myapp://export-cancelled
```

### Pattern 4: Document App Intent Workflow

When user asks how to use their App Intents in Shortcuts:

Provide a step-by-step guide:
1. Open Shortcuts app
2. Create new shortcut
3. Add actions from their app (search for app name)
4. Chain actions by connecting outputs to inputs
5. Add system actions (Show Notification, Save File, etc.)
6. Test the workflow

### Pattern 5: Generate Test Commands

When user wants to verify shortcuts work correctly:

```bash
#!/bin/bash
# Test shortcut execution

echo "Testing: Generate Screenplay Audio"
result=$(shortcuts run "Generate Screenplay Audio" -i ~/test.fountain 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ Success: $result"
else
    echo "❌ Failed: $result"
    exit 1
fi
```

## Example Interactions

### Example 1: Create Batch Processing Script

**User**: "I want to run my 'Generate Audio' shortcut on all fountain files in a folder"

**Response**:
```bash
#!/bin/bash
# Batch generate audio for all fountain files

FOLDER="$1"
if [ -z "$FOLDER" ]; then
    FOLDER="$HOME/Screenplays"
fi

echo "Processing fountain files in: $FOLDER"

for screenplay in "$FOLDER"/*.fountain; do
    if [ -f "$screenplay" ]; then
        echo "Generating audio for: $(basename "$screenplay")"
        shortcuts run "Generate Audio" --input-path "$screenplay"

        if [ $? -eq 0 ]; then
            echo "✅ Success"
        else
            echo "❌ Failed"
        fi
        echo "---"
    fi
done

echo "Batch processing complete!"
```

Usage:
```bash
chmod +x batch-generate.sh
./batch-generate.sh ~/Documents/Screenplays
```

### Example 2: URL Scheme Integration

**User**: "How do I trigger a shortcut from my Mac app when export is done?"

**Response**:
Here's how to trigger a shortcut via URL scheme:

```swift
import AppKit

func triggerShortcutOnExportComplete(filePath: String) {
    let shortcutName = "Post Export Processing"
    let encodedName = shortcutName.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!
    let encodedPath = filePath.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!

    // Build URL with x-callback-url for success/error handling
    let urlString = """
    shortcuts://x-callback-url/run-shortcut?\
    name=\(encodedName)&\
    input=text&\
    text=\(encodedPath)&\
    x-success=myapp://export-success&\
    x-error=myapp://export-error
    """

    if let url = URL(string: urlString) {
        NSWorkspace.shared.open(url)
    }
}
```

You'll also need to register your custom URL scheme (`myapp://`) in Info.plist to receive callbacks.

### Example 3: Workflow Documentation

**User**: "How do I use my app's App Intents to create a complete workflow in Shortcuts?"

**Response**:
Here's an example workflow combining app actions with system actions:

**Workflow: "Process and Export"**

1. **Select File** (System Action)
   - File Type: Your supported file types

2. **Process Content** (Your App Action)
   - Input File: [Selected File]
   - Options: (your app's parameters)

3. **Export Result** (Your App Action)
   - Input: [Processed content from step 2]
   - Output Location: (leave empty for auto-naming)

4. **Show Notification** (System Action)
   - Title: "Export Complete"
   - Body: "File saved to: [Output from step 3]"

5. **Open File** (System Action)
   - File: [Output from step 3]

This workflow pattern:
- ✅ Prompts for input file
- ✅ Processes with your app's logic
- ✅ Exports to same folder with auto-naming
- ✅ Notifies when complete
- ✅ Opens result in default app

## Limitations

### Cannot Create/Edit .shortcut Files Directly
- iOS 15+ and macOS 12+ require cryptographic signing
- Signing algorithm is proprietary to Apple
- Manual file creation breaks the signature
- The `shortcuts sign` CLI tool is broken on macOS Sonoma/Sequoia (as of 2024-2025)

### Workarounds
1. **Use App Intents** - Let users build workflows in Shortcuts app
2. **Use CLI** - Run existing shortcuts programmatically
3. **Use URL Schemes** - Trigger shortcuts from other apps
4. **Generate Documentation** - Help users create workflows manually

## References

- [Apple Support: Shortcuts CLI](https://support.apple.com/guide/shortcuts-mac/)
- [Apple Developer: App Intents](https://developer.apple.com/documentation/appintents/)
- [Shortcuts URL Scheme Guide](https://supersonicbyte.com/blog/shortcuts-url-scheme/)
- [x-callback-url Specification](http://x-callback-url.com/)

## Key Commands Reference

```bash
# List shortcuts
shortcuts list

# Run shortcut
shortcuts run "Name"
shortcuts run "Name" -i "input"
shortcuts run "Name" --input-path /path/to/file

# Run with output capture
result=$(shortcuts run "Name" 2>&1)

# View details
shortcuts view "Name"

# Sign shortcut (broken on Sonoma/Sequoia)
shortcuts sign -i unsigned.shortcut -o signed.shortcut
```

## Best Practices

1. **Always URL-encode parameters** in URL schemes
2. **Use absolute paths** when passing files to shortcuts
3. **Check exit codes** ($?) when running shortcuts in scripts
4. **Use x-callback-url** when you need error handling
5. **Test shortcuts manually** in Shortcuts app before automating
6. **Document workflows** for users rather than generating files
7. **Leverage App Intents** for deep integration with your app
