---
skill: ship-swift-library
description: Ship and release Swift library versions by merging PR first, bumping version, tagging from PR merge commit, and creating GitHub releases
---

# Ship Swift Library Skill

This skill handles the complete release process for Swift libraries.

**CRITICAL RULE**: ALWAYS merge the open PR FIRST, then create the release from the PR merge commit. NEVER merge development directly to main when a PR exists.

## Process Overview

You will perform the following steps in order:

### 1. Check for Open Pull Request

Check if there's an open PR from `development` to `main`:

```bash
gh pr list --base main --head development
```

**If PR exists**: Proceed to step 2 (merge it FIRST)
**If no PR**: Ask user if they want to create one

### 2. Verify CI Checks Pass

Check the PR status and ensure all required checks have passed:

```bash
gh pr checks <PR_NUMBER>
```

If any checks fail, inform the user and do not proceed. If pending, wait for completion.

### 3. Merge Pull Request FIRST

**CRITICAL**: Squash merge the PR to keep main branch history clean:

```bash
gh pr merge <PR_NUMBER> --squash --delete-branch=false
```

**Important**:
- Use `--squash` (clean single commit on main)
- Do NOT delete development branch (it's long-lived)

### 4. Pull PR Merge Commit

Fetch the PR merge commit from main:

```bash
git checkout main
git pull origin main
```

Verify you're on the PR merge commit:

```bash
git log --oneline -1
# Should show: "Merge pull request #X from ..."
```

### 5. Bump Version Number

Find the version file (usually `Sources/<LibraryName>/<LibraryName>.swift`) and increment the version:

```swift
public static let version = "X.Y.Z"  // Increment appropriately
```

Version increment rules:
- **Patch** (x.y.Z): Bug fixes, small improvements
- **Minor** (x.Y.0): New features, non-breaking changes
- **Major** (X.0.0): Breaking changes

Commit the version bump:

```bash
git add Sources/<LibraryName>/<LibraryName>.swift
git commit -m "Bump version to X.Y.Z

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 6. Push Version Bump to Development

Push the version bump to development branch first:

```bash
git checkout development
git cherry-pick <version_bump_commit>
git push origin development
```

Then merge to main (or push directly if on main):

```bash
git checkout main
git push origin main
```

### 7. Create Annotated Tag from PR Merge Commit

Tag the current commit on main (which is the PR merge + version bump):

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z: <Short description>

<Detailed release notes>

🤖 Generated with [Claude Code](https://claude.com/claude-code)"

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

### ✨ New Features

- Feature 1
- Feature 2

### 🐛 Bug Fixes

- Fix 1
- Fix 2

### 📊 Testing

- X tests passing
- CI status

### 📚 Documentation

- Updated docs

---

**Full Changelog**: https://github.com/<owner>/<repo>/compare/vX.Y.Z-1...vX.Y.Z
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

Ensure development is up to date:

```bash
git checkout development
git pull origin development
```

### 11. Summary Report

Provide final summary:

```
✅ Release vX.Y.Z Complete

- Pull Request #<NUMBER> merged to main ✅
- Version bumped to X.Y.Z ✅
- Tag vX.Y.Z created from PR merge commit ✅
- GitHub release published ✅
- Development branch synced ✅

Release URL: https://github.com/<owner>/<repo>/releases/tag/vX.Y.Z

The library is now ready for use via Swift Package Manager.
```

## Critical Rules (NEVER VIOLATE)

1. **ALWAYS merge PR FIRST** - Never `git merge development` when PR exists
2. **Tag from squash merge commit** - Ensure release is based on PR, not direct merge
3. **Use --squash** - Keep main branch history clean with single commits per PR
4. **Don't delete development** - It's a long-lived branch
5. **Push version bump to both branches** - Keep development and main in sync

## What Went Wrong Before

**WRONG FLOW** ❌:
1. `git merge development` (bypassed PR)
2. Create release
3. Merge PR (after release!)

**CORRECT FLOW** ✅:
1. Merge PR FIRST
2. Pull PR merge commit
3. Bump version
4. Tag from PR merge commit
5. Create release

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
