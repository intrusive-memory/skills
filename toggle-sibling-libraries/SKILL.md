---
name: toggle-sibling-libraries
description: Toggle a Swift Package.swift between the local-sibling-checkout development pattern and a clean remote-only release pattern. Use this skill whenever you need to flip Package.swift in or out of the `sibling(...)` helper-function pattern — for example, before tagging a release the dependencies must be pinned to remote-only, and on a fresh `-dev` development cycle they must go back to sibling-aware. Also trigger on phrases like "switch to remote deps", "remove the sibling helper", "restore sibling pattern", "make Package.swift release-ready", "flip to dev-mode deps", or any time the user references the `sibling()` helper or the `useLocalSiblings` constant. Only intrusive-memory/* dependencies participate in the sibling pattern; all other dependencies are left untouched.
allowed-tools: Bash, Read, Edit, Write
---

# Toggle Sibling Libraries

This skill rewrites `Package.swift` between two states.

**Sibling state (development branches):** intrusive-memory/* dependencies are routed through a `sibling(_:remote:from:)` helper that prefers a `../<name>` checkout when present and falls back to the remote pin. Lets a developer make coordinated changes across several intrusive-memory packages without publishing intermediate releases.

**Remote state (shipped releases):** intrusive-memory/* dependencies are plain `.package(url:..., .upToNextMajor(from: "X.Y.Z"))` calls pinned to the latest published release. The `sibling(...)` helpers, the `useLocalSiblings` constant, and any unused `import Foundation` are stripped.

The skill is bidirectional and idempotent.

## When this skill runs

- **Before tagging a release** — invoke with `--to remote`. The version-bump step in `ship-swift-library` calls this so the shipped `Package.swift` carries no developmental scaffolding.
- **After stamping the post-release `-dev` marker** — invoke with `--to sibling`. The `dev-marker` step in `ship-swift-library` calls this so the next development cycle can pick up sibling checkouts again.
- **Manually**, any time a developer wants to test a clean release-shape build, or restore the sibling pattern after editing.

## Scope rule (very important)

Only dependencies under `https://github.com/intrusive-memory/*` participate in the sibling pattern. Every other dependency (e.g. `apple/swift-argument-parser`, `marcprux/universal`) is **left untouched** in both directions. Hard-code this rule — the reason is that the sibling helper assumes a coordinated co-located checkout convention that only the intrusive-memory family observes.

If the user asks to add a non-intrusive-memory dep to the sibling pattern, push back and ask them to confirm; the convention exists for a reason and silently broadening it leads to surprising local-path resolution against unrelated repos.

## Prerequisites

```bash
test -f Package.swift || { echo "ABORT: no Package.swift in current directory"; exit 1; }
command -v gh >/dev/null || { echo "ABORT: gh CLI required to look up latest published versions"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "ABORT: gh not authenticated"; exit 1; }
```

The `gh` requirement is for resolving the latest published version of each intrusive-memory dep when flipping to remote (see "Version resolution" below). If the user is offline, fail fast — guessing or reusing the existing `from:` value risks shipping a release that depends on something older than what was just released upstream.

## Direction: `--to remote`

Goal: produce a `Package.swift` that builds cleanly from a fresh clone with no `../` siblings on disk and no environment variables set, and that pins each intrusive-memory dep to the **latest published GitHub release**.

### 1. Resolve the latest published version of each intrusive-memory dep

For every `sibling("<Name>", remote: "https://github.com/intrusive-memory/<Repo>.git", ...)` call in the file:

```bash
LATEST=$(gh api "repos/intrusive-memory/<Repo>/releases/latest" --jq '.tag_name' 2>/dev/null)
LATEST="${LATEST#v}"   # strip leading v if present
```

If `releases/latest` returns nothing, fall back to the most recent `vX.Y.Z` tag:

```bash
gh api "repos/intrusive-memory/<Repo>/tags" \
  --jq '[.[].name | select(test("^v[0-9]+\\.[0-9]+\\.[0-9]+$"))][0]'
```

If both queries come up empty, abort with a clear message naming the offending dep — shipping a release that pins an unreleased upstream is broken by definition.

### 2. Rewrite each sibling call

For the **`from:` variant** — `sibling("X", remote: "URL", from: "OLD")` — emit:

```swift
.package(url: "URL", .upToNextMajor(from: "<LATEST>"))
```

(Use the resolved `<LATEST>`, not the source-file `OLD` value. The `from:` argument in dev mode is just a floor; at ship time we move to whatever is actually published.)

For the **`branch:` variant** — `sibling("X", remote: "URL", branch: "feature-foo")` — emit the same `.upToNextMajor(from: "<LATEST>")` form, NOT a branch pin. **Then emit a loud warning** in the run summary:

```
WARNING: SwiftBruja was on a sibling branch ('feature-foo') in development.
Converted to .upToNextMajor(from: "1.6.1") (latest released tag).
The branch may carry unreleased changes that the published version does NOT have.
Verify the upstream is released before tagging this repo.
```

The reason for the warning: a development build that depended on an unreleased feature in a sibling branch will, when this repo ships, silently fall back to the older published version — which means tests that passed in dev may not exercise the same code at release.

### 3. Strip the helper functions and constant

Remove:
- The `let useLocalSiblings = ...` line and any explanatory comment block above it.
- Every preceding scaffold-let that the helper depends on. The canonical block declares `let manifestDir = ...`, `let isSPMCheckout = ...` (multi-line), and `let isCI = ...` above `useLocalSiblings`. All of these are dead code without the helper — strip them too, including the multi-line continuation of `isSPMCheckout`. (`scripts/toggle.py` recognises this whole set via `SCAFFOLD_LET_NAMES`.)
- Both `func sibling(...)` definitions.
- The `import Foundation` line **only if** no other code in the file references `Foundation`/`FileManager`/`ProcessInfo`/`NSString`. (Almost always safe to remove; double-check.)

The resulting file should look like a stock `Package.swift`: `swift-tools-version` line, `import PackageDescription`, the `let package = Package(...)` block, and that's it.

### 4. Run `swift format` if available

If the repo has a `make lint` target, run it. Otherwise leave formatting to whoever calls the skill next — don't introduce a swift-format dependency.

### 5. Verify the result builds

```bash
swift package resolve 2>&1 | tail -20
```

If resolve fails (most likely cause: a typo'd URL or a dep that genuinely has no published releases), surface the error and stop.

## Direction: `--to sibling`

Goal: take a remote-only `Package.swift` and re-introduce the sibling pattern for intrusive-memory/* deps, so the next development cycle can pick up `../<name>` checkouts.

### 1. Detect intrusive-memory deps

Find every `.package(url: "https://github.com/intrusive-memory/<Repo>.git", .upToNextMajor(from: "X.Y.Z"))` line. These are the ones to convert.

Anything else — `apple/`, `marcprux/`, custom hosts — stays exactly as-is.

### 2. Insert the helper block

If the file does not already contain `func sibling(`, prepend the canonical block immediately after `import PackageDescription` (and before `let package = Package(...)`):

```swift
import Foundation

// In CI we always pin to released remotes. Locally, prefer a sibling checkout
// at ../<name> if present so in-flight changes can be exercised end-to-end
// without publishing a release. Falls back to the remote pin if the sibling
// directory is missing, so fresh clones still build.
//
// When this manifest is evaluated as a transitive dependency inside Xcode's
// `SourcePackages/checkouts/` or SwiftPM's `.build/checkouts/`, every other
// dependency lives as a sibling in the same directory. Treating those as
// in-development local paths produces conflicting package identities, so we
// must skip the sibling shortcut in that context.
let manifestDir = (#filePath as NSString).deletingLastPathComponent
let isSPMCheckout =
  manifestDir.contains("/SourcePackages/checkouts/")
  || manifestDir.contains("/.build/checkouts/")
let isCI = ProcessInfo.processInfo.environment["CI"] == "true"
let useLocalSiblings = !isCI && !isSPMCheckout

func sibling(_ name: String, remote: String, from version: Version) -> Package.Dependency {
  let localPath = "../\(name)"
  if useLocalSiblings && FileManager.default.fileExists(atPath: localPath) {
    return .package(path: localPath)
  }
  return .package(url: remote, .upToNextMajor(from: version))
}

/// Same sibling-priority pattern as ``sibling(_:remote:from:)`` but pins to a
/// remote branch when no local sibling exists. Use only when a temporary
/// pre-release dependency on a feature branch is required; switch back to the
/// version-pinned ``sibling(_:remote:from:)`` once the upstream tags a release.
func sibling(_ name: String, remote: String, branch: String) -> Package.Dependency {
  let localPath = "../\(name)"
  if useLocalSiblings && FileManager.default.fileExists(atPath: localPath) {
    return .package(path: localPath)
  }
  return .package(url: remote, branch: branch)
}
```

If `import Foundation` is already present, don't duplicate it.

**Why the SPM-checkout guard matters.** A naive `useLocalSiblings = !CI` falsely activates when this manifest is evaluated as a transitive dependency inside `DerivedData/.../SourcePackages/checkouts/` — every other dependency lives as a sibling in the same directory there, so the existence check succeeds for every dep and the helper switches them all to unversioned `.package(path: ...)` references. Those collide with the same identities pulled in via remote URLs elsewhere in the graph and abort resolution with `Conflicting identity for ...`. The `manifestDir` / `isSPMCheckout` check disables the shortcut in that context. Don't ship a sibling helper without this guard.

### 3. Rewrite each intrusive-memory dep

`.package(url: "https://github.com/intrusive-memory/<Repo>.git", .upToNextMajor(from: "X.Y.Z"))`
becomes
`sibling("<Repo>", remote: "https://github.com/intrusive-memory/<Repo>.git", from: "X.Y.Z")`.

The `<Repo>` for the first argument is the bare repo name (last URL path segment with `.git` stripped).

The `from:` value is preserved verbatim — at flip-back time we don't know what version was originally there, and `.upToNextMajor(from: "X.Y.Z")` is the correct floor for the next dev cycle.

The `branch:` variant of `sibling` is **not** generated automatically. Going-to-sibling always produces the `from:` variant; if the developer wants a branch pin, they edit it manually after the toggle.

### 4. Verify the result resolves

```bash
swift package resolve 2>&1 | tail -20
```

Same as the other direction.

## Bundled script

Both transformations live in `scripts/toggle.py`. Prefer running it over hand-editing — the regex parsing handles whitespace, multi-line `sibling(...)` calls, and idempotency consistently.

```bash
python3 "$(dirname <skill-path>)/toggle-sibling-libraries/scripts/toggle.py" \
  --direction remote   # or: sibling
  [--package-swift Package.swift]
  [--dry-run]
```

Run with `--dry-run` first when invoked manually so the user can see the diff before it lands. The ship-swift-library callers run without `--dry-run` because the toggle is committed as part of a larger commit.

The script:
1. Parses `Package.swift` and identifies sibling calls / intrusive-memory deps.
2. Resolves `releases/latest` for each dep when going to remote (prints the resolved version map).
3. Performs the rewrite atomically (writes to a temp file then renames).
4. Returns non-zero if any required dep has no published release, or if the file is already in the requested state and `--strict` is set.
5. Emits the branch-variant warning to stderr, prefixed with `WARNING:`.

If the script is unavailable (older skill version, etc.), the SKILL.md text above is the canonical recipe and you can apply it manually with `Edit`.

## Idempotency

Running `--to remote` on an already-remote `Package.swift` is a no-op: no `sibling(` calls to find, no helpers to strip. Same for `--to sibling` on a file already in sibling state.

The script reports `already in <direction> state — no changes` and exits 0. With `--strict`, it exits 1.

## Critical rules

1. **Only intrusive-memory/* repos** — never broaden the sibling rule to other organizations without an explicit user instruction.
2. **Resolve to the latest published version when going to remote** — do NOT carry forward the `from:` value from the dev source. The dev floor is informational; ship-time pins to whatever is actually released.
3. **Convert `branch:` siblings to released `from:` pins, with a warning** — never pin a release-branch repo to a moving upstream branch. If the warning fires, the human running ship-swift-library should pause and verify the upstream is released.
4. **Never modify non-intrusive-memory dependencies** — even if they happen to use a `sibling(` helper (they shouldn't, but if a user has hand-rolled an exception, leave it alone and surface it in the run report).
5. **Never alter `Package.resolved`** — that file is managed by SPM and by `spm-package-audit`. This skill only touches `Package.swift`.
6. **Strip `import Foundation` only when safe** — if any other code references Foundation/FileManager/ProcessInfo, leave the import. (For the canonical sibling-pattern repos this is always safe; the import exists *only* for the helper.)

## How this fits with sibling skills

- `spm-package-audit` introduces and validates the sibling pattern during routine development hygiene. This skill (`toggle-sibling-libraries`) is the *release lever* that strips and restores it cleanly.
- `ship-swift-library` invokes `--to remote` during version-bump (step 3) and `--to sibling` during the post-release dev-marker step (step 11).
- The two skills are not competing: `spm-package-audit` enforces "is the sibling pattern correctly written?", while this skill enforces "is the sibling pattern present at all?"
