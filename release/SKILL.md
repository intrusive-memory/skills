---
name: release
description: Release a merged PR by tagging and creating a GitHub release. Use when asked to "release", "tag", or "create a release".
allowed-tools: Bash, Read, AskUserQuestion
---

# Release Workflow

This skill manages the release process for projects that use PR-based releases with git tags and GitHub releases.

## When to Use This Skill

Use this skill when:
- A PR has already been merged to main
- You need to tag the merge commit
- You need to create a GitHub release
- You need to sync development with main after release

## Pre-flight Checks

Before starting the release process, verify:

### 1. PR is Already Merged

```bash
# Check if there's a recently merged PR
gh pr list --state merged --limit 5 --json number,title,mergedAt,mergeCommit
```

**If no recently merged PR exists, STOP and ask: "Which PR should be released?"**

### 2. Determine Next Version Number

```bash
# Get the last tag
git fetch --tags
git describe --tags --abbrev=0 2>/dev/null || echo "No tags found"
```

The next version is always the last tag + 1:
- If last tag is `v29`, next is `v30`
- If last tag is `v1.2.3`, next is `v1.2.4`

**Ask the user to confirm the version number before proceeding.**

## Release Process

Once pre-flight checks pass:

### Step 1: Checkout main and pull the merge commit

```bash
git checkout main
git pull origin main
```

### Step 2: Verify we're on the merge commit

```bash
git log -1 --oneline
```

### Step 3: Create and push the tag

```bash
git tag -a "v<VERSION>" -m "$(cat <<'EOF'
Release v<VERSION>

<Brief description of what's in this release>

🤖 Tagged with [Claude Code](https://claude.com/claude-code)
EOF
)"

git push origin v<VERSION>
```

### Step 4: Create GitHub release

```bash
gh release create "v<VERSION>" \
  --title "v<VERSION>" \
  --notes "$(cat <<'EOF'
## What's New in v<VERSION>

<List key features/fixes in this release>

### Changes
See the [CHANGELOG](https://github.com/OWNER/REPO/blob/main/CHANGELOG.md) for detailed release notes.

## Installation

Download from the App Store or TestFlight.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Step 5: Sync development with main

```bash
git checkout development
git merge main
git push origin development
```

### Step 6: Report Success

Report:
- ✅ Released version v<VERSION>
- 📦 GitHub release: https://github.com/OWNER/REPO/releases/tag/v<VERSION>
- 🔄 Development branch synced with main

## Important Rules

1. **NEVER merge a PR in this skill** - This skill assumes PR is already merged
2. **ALWAYS ask user to confirm version number** - Don't guess
3. **ALWAYS sync development with main** - Keep branches in sync
4. **ALWAYS use annotated tags** (`git tag -a`) - Include metadata
5. **NEVER force push** - Releases are permanent

## Workflow Summary

```
1. Verify PR is merged
2. Determine next version (last tag + 1)
3. Ask user to confirm version
4. Checkout main and pull
5. Tag the merge commit
6. Push the tag
7. Create GitHub release
8. Sync development with main
```

## Example Usage

```
User: "Release PR #78"