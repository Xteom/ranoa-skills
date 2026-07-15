#!/usr/bin/env python3
"""Deterministic structural checks for repo-expert-onboarding guides."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


NON_SOURCE_LANGS = {"", "console", "mermaid", "output", "plain", "text"}
MERMAID_START_RE = re.compile(
    r"^(?:architecture-beta|block-beta|C4\w*|classDiagram|erDiagram|flowchart|gantt|"
    r"gitGraph|graph|journey|mindmap|packet-beta|pie|quadrantChart|sequenceDiagram|"
    r"stateDiagram(?:-v2)?|timeline|xychart-beta)\b"
)
LINE_ANCHOR_RE = re.compile(r"L(\d+)(?:-L(\d+))?")
COMMIT_RE = re.compile(r"(?:Commit|Revision|SHA)\s*:\s*`([0-9a-fA-F]{7,40})`", re.I)
BRANCH_RE = re.compile(r"Branch\s*:\s*`?([^`\n]+?)`?\s*$", re.I | re.M)
DATE_RE = re.compile(r"Analy[sz]ed\s*:\s*`?(\d{4}-\d{2}-\d{2})`?", re.I)
DIRTY_RE = re.compile(r"Working tree[^:\n]*:\s*([^\n]+)", re.I)
UPSTREAM_RE = re.compile(
    r"Upstream divergence\s*:\s*(?:ahead\s+(\d+)\s*,\s*behind\s+(\d+)|(unknown))",
    re.I,
)
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b|\?\?\?")


@dataclass(frozen=True)
class Fence:
    language: str
    body: str
    start_line: int
    end_line: int


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--guide", type=Path, required=True)
    parser.add_argument("--min-files", type=int, default=5)
    parser.add_argument("--min-diagrams", type=int, default=2)
    parser.add_argument("--min-source-snippets", type=int, default=2)
    parser.add_argument("--require-metadata", action="store_true")
    parser.add_argument("--require-head-match", action="store_true")
    parser.add_argument("--check-upstream", action="store_true")
    return parser.parse_args()


def split_fences(text: str) -> tuple[str, list[Fence], bool]:
    """Return prose-only text, fenced blocks, and whether fences are balanced."""
    prose: list[str] = []
    fences: list[Fence] = []
    open_char = ""
    open_len = 0
    language = ""
    body: list[str] = []
    start = 0

    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if not open_char:
            if match:
                marker = match.group(1)
                open_char, open_len = marker[0], len(marker)
                language = match.group(2).strip().split()[0].lower() if match.group(2).strip() else ""
                body, start = [], number
                prose.append("")
            else:
                prose.append(line)
            continue

        if match and match.group(1)[0] == open_char and len(match.group(1)) >= open_len:
            fences.append(Fence(language, "\n".join(body).strip(), start, number))
            open_char, open_len, language, body, start = "", 0, "", [], 0
        else:
            body.append(line)
        prose.append("")

    return "\n".join(prose), fences, not open_char


def inline_links(text: str) -> list[str]:
    """Extract inline Markdown destinations, including balanced parentheses."""
    links: list[str] = []
    index = 0
    while index < len(text):
        left = text.find("[", index)
        if left < 0:
            break
        right = text.find("]", left + 1)
        if right < 0 or right + 1 >= len(text) or text[right + 1] != "(":
            index = left + 1
            continue
        cursor, depth, escaped = right + 2, 1, False
        while cursor < len(text) and depth:
            char = text[cursor]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            cursor += 1
        if depth:
            index = left + 1
            continue
        raw = text[right + 2 : cursor - 1].strip()
        if raw.startswith("<") and ">" in raw:
            destination = raw[1 : raw.index(">")]
        else:
            destination = re.split(r"\s+[\"']", raw, maxsplit=1)[0]
        links.append(destination.replace("\\ ", " "))
        index = cursor
    return links


def heading_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    prose, _, _ = split_fences(text)
    lines = prose.splitlines()
    titles: list[str] = []
    for index, line in enumerate(lines):
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            titles.append(match.group(1))
        elif index + 1 < len(lines) and re.match(r"^\s*(?:=+|-+)\s*$", lines[index + 1]) and line.strip():
            titles.append(line.strip())
    for raw_title in titles:
        title = re.sub(r"!?(?:\[([^]]+)\]\([^)]+\))", r"\1", raw_title)
        title = re.sub(r"<[^>]+>", "", title)
        title = re.sub(r"[`*_~]", "", title).strip().lower()
        slug = re.sub(r"[^\w\- ]", "", title, flags=re.UNICODE).replace(" ", "-")
        suffix = counts.get(slug, 0)
        counts[slug] = suffix + 1
        anchors.add(slug if suffix == 0 else f"{slug}-{suffix}")
    return anchors


def local_target(document: Path, destination: str) -> tuple[Path, str] | None:
    if destination.startswith(("http://", "https://", "mailto:")):
        return None
    path_part, _, fragment = destination.partition("#")
    linked = document if not path_part else (document.parent / unquote(path_part)).resolve()
    return linked, unquote(fragment)


def normalized_source(text: str) -> str:
    return "\n".join(line.rstrip() for line in textwrap.dedent(text).strip().splitlines())


def snippet_has_source_link(document: Path, prose_lines: list[str], fence: Fence, repo: Path) -> bool:
    start = max(0, fence.start_line - 7)
    end = min(len(prose_lines), fence.end_line + 6)
    nearby = "\n".join(prose_lines[start:end])
    if not re.search(r"\bSource\s*:", nearby, re.I):
        return False
    snippet = normalized_source(fence.body)
    for destination in inline_links(nearby):
        target = local_target(document, destination)
        if not target:
            continue
        linked, fragment = target
        try:
            linked.relative_to(repo)
        except ValueError:
            continue
        if not linked.is_file():
            continue
        source_lines = linked.read_text(encoding="utf-8", errors="ignore").splitlines()
        anchor = LINE_ANCHOR_RE.fullmatch(fragment)
        if anchor:
            first = int(anchor.group(1)) - 1
            last = int(anchor.group(2) or len(source_lines))
            source_lines = source_lines[first:last]
        if snippet and snippet in normalized_source("\n".join(source_lines)):
            return True
    return False


def main() -> int:
    args = parse_args()
    repo, guide = args.repo.resolve(), args.guide.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not repo.is_dir():
        errors.append(f"repository does not exist: {repo}")
    if not guide.is_dir():
        errors.append(f"guide does not exist: {guide}")
    if errors:
        return report(errors, warnings, 0, 0, 0, 0)

    markdown = sorted(guide.glob("*.md"))
    if len(markdown) < args.min_files:
        errors.append(f"found {len(markdown)} Markdown files; require {args.min_files}")
    readme = guide / "README.md"
    if not readme.exists():
        errors.append("guide has no README.md index")

    texts: dict[Path, str] = {}
    prose_texts: dict[Path, str] = {}
    diagrams = snippets = local_link_count = 0

    for document in markdown:
        text = document.read_text(encoding="utf-8")
        prose, fences, balanced = split_fences(text)
        texts[document], prose_texts[document] = text, prose
        if not balanced:
            errors.append(f"{document.name}: unbalanced fenced code block")
        placeholders = sorted(set(PLACEHOLDER_RE.findall(prose)))
        if placeholders:
            errors.append(f"{document.name}: contains prose placeholders: {placeholders}")

        prose_lines = prose.splitlines()
        diagrams += sum(
            f.language == "mermaid" and bool(MERMAID_START_RE.match(f.body)) for f in fences
        )
        snippets += sum(
            f.language not in NON_SOURCE_LANGS
            and bool(f.body)
            and snippet_has_source_link(document, prose_lines, f, repo)
            for f in fences
        )

        for destination in inline_links(prose):
            target = local_target(document, destination)
            if not target:
                continue
            local_link_count += 1
            linked, fragment = target
            if not linked.exists():
                errors.append(f"{document.name}: missing link target {destination}")
                continue
            if not fragment:
                continue
            line_anchor = LINE_ANCHOR_RE.fullmatch(fragment)
            if line_anchor and linked.is_file():
                start_line = int(line_anchor.group(1))
                end_line = int(line_anchor.group(2) or start_line)
                line_count = sum(1 for _ in linked.open(encoding="utf-8", errors="ignore"))
                if start_line < 1 or end_line < start_line or end_line > line_count:
                    errors.append(f"{document.name}: invalid line anchor {destination}")
            elif linked.suffix.lower() == ".md" and fragment not in heading_anchors(
                linked.read_text(encoding="utf-8")
            ):
                errors.append(f"{document.name}: missing heading anchor {destination}")

    if diagrams < args.min_diagrams:
        errors.append(f"found {diagrams} non-empty Mermaid diagrams; require {args.min_diagrams}")
    if snippets < args.min_source_snippets:
        errors.append(
            f"found {snippets} non-empty source snippets with nearby source links; "
            f"require {args.min_source_snippets}"
        )

    index = texts.get(readme, "")
    if readme.exists():
        indexed: set[Path] = set()
        for destination in inline_links(prose_texts[readme]):
            target = local_target(readme, destination)
            if target and target[0].suffix.lower() == ".md":
                indexed.add(target[0])
        for document in markdown:
            if document != readme and document not in indexed:
                errors.append(f"README.md does not link to {document.name}")

        commit_match = COMMIT_RE.search(index)
        if not commit_match:
            errors.append("README.md does not declare `Commit: `<sha>``")
        if args.require_metadata:
            for label, pattern in (
                ("branch", BRANCH_RE), ("analyzed date", DATE_RE),
                ("working-tree state", DIRTY_RE), ("upstream divergence", UPSTREAM_RE),
            ):
                if not pattern.search(index):
                    errors.append(f"README.md does not declare {label}")
            branch = BRANCH_RE.search(index)
            actual_branch = git(repo, "branch", "--show-current")
            if branch and actual_branch.returncode == 0:
                declared_branch = branch.group(1).strip()
                current_branch = actual_branch.stdout.strip()
                if current_branch and declared_branch != current_branch:
                    errors.append(
                        f"declared branch {declared_branch} does not match {current_branch}"
                    )
                elif not current_branch and declared_branch.lower() not in {"detached", "detached head"}:
                    errors.append("detached HEAD must be declared as Branch: detached")
            analyzed = DATE_RE.search(index)
            if analyzed:
                try:
                    dt.date.fromisoformat(analyzed.group(1))
                except ValueError:
                    errors.append(f"README.md has invalid analyzed date {analyzed.group(1)}")
            dirty = DIRTY_RE.search(index)
            if dirty and not re.search(r"\b(?:clean|dirty|modified|untracked)\b", dirty.group(1), re.I):
                errors.append("README.md working-tree state must say clean, dirty, modified, or untracked")
        if args.require_head_match and commit_match:
            head = git(repo, "rev-parse", "HEAD")
            if head.returncode:
                errors.append(f"cannot read repository HEAD: {head.stderr.strip()}")
            elif not head.stdout.strip().lower().startswith(commit_match.group(1).lower()):
                errors.append(
                    f"guide commit {commit_match.group(1)} does not match HEAD {head.stdout.strip()}"
                )

    if args.check_upstream:
        upstream = git(repo, "rev-parse", "--abbrev-ref", "@{upstream}")
        if upstream.returncode:
            warnings.append("repository has no configured upstream; freshness was not checked")
            declared = UPSTREAM_RE.search(index)
            if args.require_metadata and declared and not declared.group(3):
                errors.append("README.md must record upstream divergence as unknown when no upstream exists")
        else:
            counts = git(repo, "rev-list", "--left-right", "--count", "HEAD...@{upstream}")
            if counts.returncode:
                warnings.append(f"cannot compare upstream: {counts.stderr.strip()}")
            else:
                ahead, behind = (int(value) for value in counts.stdout.split())
                declared = UPSTREAM_RE.search(index)
                if not declared or declared.group(3):
                    errors.append(
                        f"README.md must record upstream divergence: ahead {ahead}, behind {behind}"
                    )
                elif (int(declared.group(1)), int(declared.group(2))) != (ahead, behind):
                    errors.append(
                        f"declared upstream divergence does not match local refs: ahead {ahead}, behind {behind}"
                    )
                if ahead or behind:
                    warnings.append(
                        f"HEAD differs from {upstream.stdout.strip()}: ahead {ahead}, behind {behind}; "
                        "remote refs may be stale"
                    )

    return report(errors, warnings, len(markdown), local_link_count, diagrams, snippets)


def report(
    errors: list[str], warnings: list[str], markdown_count: int,
    link_count: int, diagram_count: int, snippet_count: int,
) -> int:
    print(
        f"files={markdown_count} local_links={link_count} diagrams={diagram_count} "
        f"source_snippets={snippet_count}"
    )
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
