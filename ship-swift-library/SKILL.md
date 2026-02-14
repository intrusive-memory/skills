---
name: ship-swift-library
description: Ship and release Swift library versions by bumping the version on development, merging the PR once CI passes, then tagging and creating a GitHub release from main
allowed-tools: Bash, Read, Grep, Glob, Edit, Skill
dependencies:
  - organize-agent-docs
---

# Ship Swift Library Skill

This skill handles the complete release process for Swift libraries.

**CRITICAL RULE**: Bump the version on `development` BEFORE merging the PR. The version bump ships as part of the PR merge to `main`. NEVER merge development directly to main when a PR exists.

## Process Overview

You will perform the following steps in order:

### 1. Check for Open Pull Request

Check if there's an open PR from `development` to `main`:

```bash
gh pr list --base main --head development
```

**If PR exists**: Proceed to step 2
**If no PR**: Ask user if they want to create one

### 2. Determine Version Number

Find the current version (usually `Sources/<LibraryName>/<LibraryName>.swift`):

```swift
public static let version = "X.Y.Z"
```

Ask the user what version this release should be. Version increment rules:
- **Patch** (x.y.Z): Bug fixes, small improvements
- **Minor** (x.Y.0): New features, non-breaking changes
- **Major** (X.0.0): Breaking changes

### 3. Bump Version and Audit Documentation

Make sure you're on the `development` branch, then update the version:

```bash
git checkout development
git pull origin development
```

Edit the version file (e.g. `Sources/<LibraryName>/<LibraryName>.swift`).

**Then organize and update project documentation** using the organize-agent-docs skill:

```
/organize-agent-docs
```

This will:
- Ensure AGENTS.md contains universal project documentation (architecture, APIs, dependencies)
- Ensure CLAUDE.md contains only Claude-specific instructions (tool preferences, build requirements)
- Ensure GEMINI.md contains only Gemini-specific instructions
- Update version numbers across all documentation
- Verify documentation structure follows best practices
- Check that agent-specific files properly reference AGENTS.md

**After running organize-agent-docs**, also update README.md:
- Update version numbers in installation examples
- Verify all code examples work with current API
- Add new features to feature list
- Update platform requirements (iOS/macOS/Swift/Xcode versions)
- Verify all doc links point to existing files

Commit everything together — version bump + doc updates — in a single commit:

```bash
git add Sources/<LibraryName>/<LibraryName>.swift README.md AGENTS.md CLAUDE.md GEMINI.md
git commit -m "Bump version to X.Y.Z and update documentation

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
git push origin development
```

**Important**: The version bump and doc updates are now part of the PR diff and will be included when the PR is merged.

### 4. Verify CI Checks Pass

Wait for CI to run on the updated PR (the version bump push triggers a new CI run):

```bash
gh pr checks <PR_NUMBER>
```

If any checks fail, inform the user and do not proceed. If checks are pending, poll until they complete:

```bash
gh pr checks <PR_NUMBER> --watch
```

### 5. Merge Pull Request

**CRITICAL**: Squash merge the PR to keep main branch history clean:

```bash
gh pr merge <PR_NUMBER> --squash --delete-branch=false
```

**Important**:
- Use `--squash` (clean single commit on main)
- Do NOT delete development branch (it's long-lived)
- The squash commit on main now contains the version bump

### 6. Pull Merge Commit to Local Main

```bash
git checkout main
git pull origin main
```

Verify you're on the squash merge commit:

```bash
git log --oneline -1
```

### 7. Create Annotated Tag on Main

Tag the squash merge commit on main:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z: <Short description>

<Detailed release notes>

Generated with [Claude Code](https://claude.com/claude-code)"

git push origin vX.Y.Z
```

### 8. Create GitHub Release

Create a GitHub release from the tag:

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z: <Title>" \
  --notes "$(cat <<'EOF'
# <Library Name> vX.Y.Z

## <Emoji> <Feature Category>

<Description of what this release adds>

### New Features

- Feature 1
- Feature 2

### Bug Fixes

- Fix 1
- Fix 2

### Testing

- X tests passing
- CI status

### Documentation

- Updated docs

---

**Full Changelog**: https://github.com/<owner>/<repo>/compare/vPREVIOUS...vX.Y.Z
EOF
)"
```

### 9. Verify Release

Confirm the release was created successfully:

```bash
gh release view vX.Y.Z --json tagName,targetCommitish,url
```

Verify:
- Tag is `vX.Y.Z`
- Target is `main` branch
- URL is accessible

### 10. Sync Development Branch

Ensure development has the squash merge from main (avoids future merge conflicts):

```bash
git checkout development
git merge origin/main
git push origin development
```

### 11. Summary Report

Provide final summary:

```
Release vX.Y.Z Complete

- Version bumped to X.Y.Z on development ✅
- Documentation organized with /organize-agent-docs ✅
  - AGENTS.md: Universal project documentation
  - CLAUDE.md: Claude-specific instructions only
  - GEMINI.md: Gemini-specific instructions only
- README.md updated (user-facing documentation) ✅
- CI checks passed ✅
- Pull Request #<NUMBER> merged to main (includes version bump + docs) ✅
- Tag vX.Y.Z created on main ✅
- GitHub release published ✅
- Development branch synced with main ✅

Release URL: https://github.com/<owner>/<repo>/releases/tag/vX.Y.Z

The library is now ready for use via Swift Package Manager.
```

## Critical Rules (NEVER VIOLATE)

1. **Bump version BEFORE merging** - The version bump must be part of the PR
2. **Organize docs with /organize-agent-docs** - Ensure proper separation of universal vs agent-specific documentation
3. **Wait for CI after version bump** - Don't merge until the new CI run passes
4. **Use --squash** - Keep main branch history clean with single commits per PR
5. **Don't delete development** - It's a long-lived branch
6. **Tag on main after merge** - The tag goes on the squash merge commit
7. **Sync development after release** - Merge main back to avoid future conflicts

## Correct Flow

```
development: [features] -> [version bump] -> [/organize-agent-docs] -> (CI passes) -> PR merged
main:        -----------------------------------------------------------------> [squash commit] -> [tag vX.Y.Z] -> [release]
development: [merge main back] ------------------------------------------------->
```

## Error Handling

If any step fails:
1. Stop immediately
2. Explain what failed and why
3. Provide fix guidance
4. Do not proceed

## Notes

- Requires GitHub CLI (`gh`) authenticated
- Requires git configured with merge permissions
- All commits include Claude Code attribution
