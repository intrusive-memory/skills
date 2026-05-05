#!/usr/bin/env python3
"""Toggle Package.swift between sibling and remote dependency patterns.

The sibling pattern routes intrusive-memory/* deps through a `sibling(...)`
helper that prefers a `../<name>` checkout if present. The remote pattern
emits plain `.package(url:..., .upToNextMajor(from:))` calls pinned to the
latest published release.

Only intrusive-memory/* dependencies participate in this toggle.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Two pieces — `import Foundation` belongs ABOVE `import PackageDescription`,
# while the helper functions and `useLocalSiblings` constant belong BELOW it.
CANONICAL_FOUNDATION_IMPORT = "import Foundation\n"

CANONICAL_HELPER_BLOCK = """
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
  let localPath = "../\\(name)"
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
  let localPath = "../\\(name)"
  if useLocalSiblings && FileManager.default.fileExists(atPath: localPath) {
    return .package(path: localPath)
  }
  return .package(url: remote, branch: branch)
}
"""

# Names of `let <name> = ...` variables that belong to the sibling-helper
# scaffolding. These are removed wholesale (along with their continuation
# lines and the comment block above them) when flipping to remote.
SCAFFOLD_LET_NAMES = {
    "manifestDir",
    "isSPMCheckout",
    "isCI",
    "useLocalSiblings",
}

INTRUSIVE_MEMORY_HOST = "https://github.com/intrusive-memory/"

SIBLING_FROM_RE = re.compile(
    r'sibling\(\s*"(?P<name>[^"]+)"\s*,\s*'
    r'remote:\s*"(?P<remote>[^"]+)"\s*,\s*'
    r'from:\s*"(?P<from>[^"]+)"\s*\)',
    re.DOTALL,
)

SIBLING_BRANCH_RE = re.compile(
    r'sibling\(\s*"(?P<name>[^"]+)"\s*,\s*'
    r'remote:\s*"(?P<remote>[^"]+)"\s*,\s*'
    r'branch:\s*"(?P<branch>[^"]+)"\s*\)',
    re.DOTALL,
)

PACKAGE_URL_INTRUSIVE_RE = re.compile(
    r'\.package\(\s*'
    r'url:\s*"(?P<remote>https://github\.com/intrusive-memory/(?P<repo>[^"/]+?)\.git)"\s*,\s*'
    r'\.upToNextMajor\(\s*from:\s*"(?P<from>[^"]+)"\s*\)\s*'
    r'\)',
    re.DOTALL,
)


@dataclass
class ToggleReport:
    direction: str
    converted: list[tuple[str, str, str]]  # (name, old_descriptor, new_descriptor)
    warnings: list[str]
    no_op: bool = False
    package_swift: Path = Path("Package.swift")

    def emit(self, *, json_out: bool) -> None:
        if json_out:
            payload = {
                "direction": self.direction,
                "no_op": self.no_op,
                "package_swift": str(self.package_swift),
                "converted": [
                    {"name": n, "from": o, "to": t} for n, o, t in self.converted
                ],
                "warnings": self.warnings,
            }
            print(json.dumps(payload, indent=2))
            return

        if self.no_op:
            print(f"Package.swift already in {self.direction} state — no changes.")
            return

        print(f"Toggled Package.swift to {self.direction} state.")
        if self.converted:
            print("\nConverted dependencies:")
            for name, old, new in self.converted:
                print(f"  - {name}")
                print(f"      {old}")
                print(f"   -> {new}")
        for w in self.warnings:
            print(f"\nWARNING: {w}", file=sys.stderr)


def gh_latest_release(repo: str) -> str | None:
    """Return the latest published version of intrusive-memory/<repo>, no leading v."""
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/intrusive-memory/{repo}/releases/latest", "--jq", ".tag_name"],
            capture_output=True, text=True, check=False,
        )
        tag = out.stdout.strip()
        if tag:
            return tag.lstrip("v")
    except FileNotFoundError:
        return None

    # Fallback: most recent semver tag
    out = subprocess.run(
        [
            "gh", "api", f"repos/intrusive-memory/{repo}/tags",
            "--jq", '[.[].name | select(test("^v[0-9]+\\\\.[0-9]+\\\\.[0-9]+$"))][0]',
        ],
        capture_output=True, text=True, check=False,
    )
    tag = out.stdout.strip()
    if tag and tag != "null":
        return tag.lstrip("v")
    return None


def detect_state(text: str) -> str:
    """Return 'sibling' if helper functions are present, else 'remote'."""
    if "func sibling(" in text or "useLocalSiblings" in text:
        return "sibling"
    return "remote"


def strip_scaffold(text: str) -> str:
    """Remove the helper block: comment block, scaffold-let variables, and both sibling helpers.

    Conservative: only strips between the FIRST recognised scaffold-let line (or the
    comment block immediately above it) and the closing brace of the LAST `func sibling`.
    User code outside that range is preserved.
    """
    lines = text.splitlines(keepends=True)

    # Find the anchor: `let useLocalSiblings` is required for the helper to function,
    # so its presence confirms we're looking at a sibling-pattern Package.swift.
    has_useLocalSiblings = any(
        ln.lstrip().startswith("let useLocalSiblings") for ln in lines
    )
    if not has_useLocalSiblings:
        return text

    # Find the FIRST scaffold-let line. The helper block starts at (or just above) this line.
    # Walking forward from the top of the file is safer than walking back from
    # `let useLocalSiblings`, because user-defined `let` statements that happen to live
    # between imports and the helper block won't be falsely consumed.
    first_scaffold_let_idx = next(
        (
            i for i, ln in enumerate(lines)
            if (m := re.match(r"^\s*let\s+(\w+)\b", ln)) and m.group(1) in SCAFFOLD_LET_NAMES
        ),
        None,
    )
    if first_scaffold_let_idx is None:
        return text

    # Walk back from the first scaffold-let through the explanatory `//` comment block.
    # Do NOT consume the blank line above — it separates the helper block from the imports
    # and stripping it would glue `import PackageDescription` to `let package = Package(`.
    start = first_scaffold_let_idx
    while start - 1 >= 0 and lines[start - 1].lstrip().startswith("//"):
        start -= 1

    # Find the closing brace of the LAST `func sibling`. We use brace depth from the
    # first scaffold-let forward; everything between start and last_brace+1 is the
    # helper block (scaffold lets, continuation lines, helper functions, doc comments).
    last_brace = None
    depth = 0
    in_func = False
    for i in range(first_scaffold_let_idx, len(lines)):
        ln = lines[i]
        if "func sibling(" in ln:
            in_func = True
        if in_func:
            depth += ln.count("{") - ln.count("}")
            if depth == 0 and "{" in "".join(lines[first_scaffold_let_idx : i + 1]):
                last_brace = i
                in_func = False
    if last_brace is None:
        return text

    end = last_brace + 1
    # Eat one trailing blank line if present
    if end < len(lines) and lines[end].strip() == "":
        end += 1

    new_lines = lines[:start] + lines[end:]
    new_text = "".join(new_lines)

    # Drop `import Foundation` if Foundation/FileManager/ProcessInfo are no longer referenced
    if not re.search(r"\b(FileManager|ProcessInfo|NSString|URLSession|UserDefaults|Bundle|Date|Data|FileHandle)\b", new_text):
        new_text = re.sub(r"^import Foundation[^\n]*\n", "", new_text, count=1, flags=re.MULTILINE)

    # Collapse runs of 3+ blank lines to 2
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)
    return new_text


def insert_scaffold(text: str) -> str:
    """Insert `import Foundation` (above PackageDescription) and the helper block (below)."""
    if "func sibling(" in text:
        return text  # already present

    needle = "import PackageDescription\n"
    idx = text.find(needle)
    if idx == -1:
        raise RuntimeError("Package.swift missing `import PackageDescription` — cannot insert helper block.")

    # Place `import Foundation` above `import PackageDescription` if not already present.
    # Convention in the canonical files: Foundation first, then PackageDescription.
    if "import Foundation" not in text:
        text = text[:idx] + CANONICAL_FOUNDATION_IMPORT + text[idx:]
        idx += len(CANONICAL_FOUNDATION_IMPORT)

    insert_at = idx + len(needle)
    # The block already starts with `\n` (creates a blank line after the import) and ends with `\n`.
    # text[insert_at:] typically starts with `\nlet package = Package(...`, which provides the trailing blank.
    # Don't add additional newlines or we'll double-blank.
    return text[:insert_at] + CANONICAL_HELPER_BLOCK + text[insert_at:]


def to_remote(text: str, *, resolve_versions: bool) -> tuple[str, ToggleReport]:
    report = ToggleReport(direction="remote", converted=[], warnings=[])

    # Resolve a version per intrusive-memory dep we're about to convert
    needed_repos: set[str] = set()
    for m in SIBLING_FROM_RE.finditer(text):
        if m.group("remote").startswith(INTRUSIVE_MEMORY_HOST):
            needed_repos.add(_repo_from_remote(m.group("remote")))
    for m in SIBLING_BRANCH_RE.finditer(text):
        if m.group("remote").startswith(INTRUSIVE_MEMORY_HOST):
            needed_repos.add(_repo_from_remote(m.group("remote")))

    if not needed_repos:
        report.no_op = True
        return text, report

    versions: dict[str, str] = {}
    if resolve_versions:
        for repo in sorted(needed_repos):
            v = gh_latest_release(repo)
            if not v:
                raise RuntimeError(
                    f"Could not resolve a published release for intrusive-memory/{repo}. "
                    f"Either the repo has no releases yet (cannot ship pinned to it) "
                    f"or `gh` is not authenticated."
                )
            versions[repo] = v

    def _from_replacer(m: re.Match) -> str:
        remote = m.group("remote")
        name = m.group("name")
        old_from = m.group("from")
        if not remote.startswith(INTRUSIVE_MEMORY_HOST):
            return m.group(0)  # leave foreign deps alone (shouldn't happen)
        repo = _repo_from_remote(remote)
        new_from = versions.get(repo, old_from) if resolve_versions else old_from
        new = f'.package(url: "{remote}", .upToNextMajor(from: "{new_from}"))'
        report.converted.append(
            (name, f'sibling(... from: "{old_from}")', f'.upToNextMajor(from: "{new_from}")')
        )
        return new

    def _branch_replacer(m: re.Match) -> str:
        remote = m.group("remote")
        name = m.group("name")
        branch = m.group("branch")
        if not remote.startswith(INTRUSIVE_MEMORY_HOST):
            return m.group(0)
        repo = _repo_from_remote(remote)
        new_from = versions.get(repo) if resolve_versions else None
        if not new_from:
            raise RuntimeError(
                f"Sibling branch dep {name} ({repo}) needs a published version to flip to remote."
            )
        new = f'.package(url: "{remote}", .upToNextMajor(from: "{new_from}"))'
        report.converted.append(
            (name, f'sibling(... branch: "{branch}")', f'.upToNextMajor(from: "{new_from}")')
        )
        report.warnings.append(
            f"{name} was on a sibling branch ('{branch}') in development. "
            f"Converted to .upToNextMajor(from: \"{new_from}\") (latest released tag). "
            f"The branch may carry unreleased changes that the published version does NOT have. "
            f"Verify upstream is released before tagging this repo."
        )
        return new

    new_text = SIBLING_FROM_RE.sub(_from_replacer, text)
    new_text = SIBLING_BRANCH_RE.sub(_branch_replacer, new_text)
    new_text = strip_scaffold(new_text)
    return new_text, report


def to_sibling(text: str) -> tuple[str, ToggleReport]:
    report = ToggleReport(direction="sibling", converted=[], warnings=[])

    matches = list(PACKAGE_URL_INTRUSIVE_RE.finditer(text))
    if not matches and "func sibling(" in text:
        report.no_op = True
        return text, report

    def _replacer(m: re.Match) -> str:
        # Detect the indent of the line that holds the `.package(` so the
        # reconstructed `sibling(...)` matches the surrounding style.
        line_start = text.rfind("\n", 0, m.start()) + 1
        indent = text[line_start : m.start()]
        inner = indent + "  "
        repo = m.group("repo")
        remote = m.group("remote")
        old_from = m.group("from")
        new = (
            f'sibling(\n{inner}"{repo}",\n'
            f'{inner}remote: "{remote}",\n'
            f'{inner}from: "{old_from}")'
        )
        report.converted.append(
            (repo, f'.upToNextMajor(from: "{old_from}")', f'sibling(... from: "{old_from}")')
        )
        return new

    new_text = PACKAGE_URL_INTRUSIVE_RE.sub(_replacer, text)

    if report.converted or "func sibling(" not in new_text:
        new_text = insert_scaffold(new_text)

    return new_text, report


def _repo_from_remote(remote: str) -> str:
    # https://github.com/intrusive-memory/SwiftBruja.git -> SwiftBruja
    last = remote.rstrip("/").rsplit("/", 1)[-1]
    return last[:-4] if last.endswith(".git") else last


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--direction", choices=["remote", "sibling"], required=True)
    p.add_argument("--package-swift", default="Package.swift", type=Path)
    p.add_argument("--dry-run", action="store_true", help="Print the new file without writing")
    p.add_argument("--strict", action="store_true", help="Exit non-zero if no changes were needed")
    p.add_argument("--no-resolve", action="store_true",
                   help="Skip `gh` lookup; reuse existing from: values (test/offline only)")
    p.add_argument("--json", action="store_true", help="Emit a machine-readable report")
    args = p.parse_args()

    path: Path = args.package_swift
    if not path.exists():
        print(f"ABORT: {path} does not exist", file=sys.stderr)
        return 2

    text = path.read_text()

    try:
        if args.direction == "remote":
            new_text, report = to_remote(text, resolve_versions=not args.no_resolve)
        else:
            new_text, report = to_sibling(text)
    except RuntimeError as e:
        print(f"ABORT: {e}", file=sys.stderr)
        return 2

    report.package_swift = path

    if args.dry_run:
        if not report.no_op:
            sys.stdout.write(new_text)
        report.emit(json_out=args.json)
        return 0

    if not report.no_op:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(new_text)
        tmp.replace(path)

    report.emit(json_out=args.json)

    if report.no_op and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
