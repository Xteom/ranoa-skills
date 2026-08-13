#!/usr/bin/env python3
"""Deterministic structural checks for repo-expert-onboarding guides."""

from __future__ import annotations

import argparse
import datetime as dt
import os
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
LINE_ANCHOR_RE = re.compile(r"L(\d+)(?:C\d+)?(?:-L(\d+)(?:C\d+)?)?")
COMMIT_RE = re.compile(r"(?:Commit|Revision|SHA)\s*:\s*\**`?([0-9a-fA-F]{7,40})\b`?", re.I)
BRANCH_RE = re.compile(r"Branch\s*:\s*\**`?([^`*\s]+)", re.I)
DATE_RE = re.compile(r"Analy[sz]ed\s*:\s*`?(\d{4}-\d{2}-\d{2})`?", re.I)
DIRTY_RE = re.compile(r"Working tree[^:\n]*:\s*([^\n]+)", re.I)
UPSTREAM_RE = re.compile(
    r"Upstream divergence\s*:\s*(?:ahead\s+(\d+)\s*,\s*behind\s+(\d+)|(unknown))",
    re.I,
)
# Deliberately case-sensitive: lowercase "todo"/"placeholder" are common domain
# words in guides (agent todo lists, config placeholder preservation).
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b|\?\?\?")
NUMBERED_RE = re.compile(r"^(\d+[a-z]?)-(.+)$")
GENERIC_STEMS = {
    "big-picture", "setup-entrypoints-and-configuration", "runtime-flow",
    "core-domain-model", "state-storage-memory-and-context",
    "tools-integrations-and-extension-points", "user-interfaces-apis-and-clients",
    "uis-apis-and-clients", "security-permissions-and-trust-model",
    "testing-debugging-and-observability", "change-playbooks",
}
REQUIRED_FILES = ("appendix-code-map.md", "appendix-coverage-and-evidence.md")
REFDEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*<?(\S+?)>?(?:\s+[\"'(].*)?$", re.M)
MIN_SNIPPET_LINES = 3
MIN_SNIPPET_CHARS = 80
MIN_DIAGRAM_LINES = 3
MIN_NUMBERED_WORDS = 50

# ---- Self-containment (inward) and coverage-accuracy (outward) checks ----
# Design: precision over recall. Deterministic checks gate only what they can
# see reliably; judgment calls (thin glosses, wrong-model traps, two-sense
# terms) belong to the critic, never to this script.
ORPHAN_MIN_FILES = 3          # concept used in >= N numbered files with no definition
FORWARD_GAP_MIN_DISTANCE = 2  # gate gaps of >= N files; distance 1 is a warning
GLOSS_WINDOW_CHARS = 60       # how far after a use a parenthetical gloss may start
COPULA_TOKEN_WINDOW = 4       # tokens between concept and is/are for definition shape
MIN_WAIVER_SUBSTANCE = 40     # chars of justification beyond the quoted gloss
LOC_TOLERANCE = 0.20          # relative error allowed on cited line counts
LOC_MIN_CLAIM = 50            # ignore tiny cited counts; +/-20% of 14 is noise
SC_SECTION_MIN_WORDS = 30
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]{2,}")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*")
COPULAS = {"is", "are", "means", "was", "were"}
STOPWORDS = {
    "a", "all", "also", "an", "and", "any", "are", "as", "at", "be", "been",
    "being", "both", "but", "by", "can", "cannot", "code", "could", "doc",
    "docs", "does", "doing", "done", "each", "for", "from", "had", "has",
    "have", "how", "in", "into", "is", "it", "its", "less", "may", "might",
    "more", "most", "must", "no", "not", "notes", "of", "on", "only", "or",
    "other", "over", "per", "shall", "should", "some", "such", "than", "that",
    "the", "then", "these", "they", "this", "those", "to", "under", "versus",
    "via", "vs", "was", "were", "what", "when", "where", "which", "why",
    "will", "with", "would", "your",
}
WAIVER_RE = re.compile(r"^\s*(?:[-*]\s+)?waiver\s*:\s*`([^`]+)`(.*)$", re.I)
LOC_CELL_RE = re.compile(r"^~?\s*(\d[\d,]*)\s*(k?)$", re.I)
PATH_CELL_RE = re.compile(r"^[\w./-]+(?:/|\.[A-Za-z]{1,4})$")
CODE_EXTS = {
    ".c", ".cc", ".cpp", ".cs", ".go", ".h", ".java", ".js", ".jsx", ".kt",
    ".mjs", ".php", ".py", ".rb", ".rs", ".swift", ".ts", ".tsx",
}
SCAN_EXCLUDE_DIRS = {
    ".git", "node_modules", "dist", "build", "vendor", "target", ".venv",
    "venv", "__pycache__", ".next", "coverage",
}
TEST_PATH_RE = re.compile(r"(?:^|[/._-])(?:tests?|specs?|__tests__)(?:[/._-]|$)", re.I)
CLI_CMD_RES = (
    re.compile(r"\.command\(\s*['\"]([a-z][a-z0-9-]{3,})(?:\s+[^'\"]*)?['\"]"),
    re.compile(r"add_parser\(\s*['\"]([a-z][a-z0-9_-]{3,})['\"]"),
)


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
    parser.add_argument("--loc-tolerance", type=float, default=LOC_TOLERANCE)
    parser.add_argument("--skip-cli-scan", action="store_true")
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


def reference_links(text: str) -> list[str]:
    """Resolve reference-style links: [text][label] and collapsed [label][]."""
    refdefs = {
        match.group(1).strip().lower(): match.group(2)
        for match in REFDEF_RE.finditer(text)
    }
    destinations: list[str] = []
    for match in re.finditer(r"\[([^\]]+)\]\[([^\]]*)\]", text):
        label = (match.group(2) or match.group(1)).strip().lower()
        if label in refdefs:
            destinations.append(refdefs[label])
    return destinations


def local_links(text: str) -> list[str]:
    return inline_links(text) + reference_links(text)


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
        # Strip code/emphasis markup but keep underscores: GitHub slugs preserve
        # them, and code-identifier headings (run_agent) are common in guides.
        title = re.sub(r"[`*~]", "", title).strip().lower()
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


def mermaid_kind(body: str) -> str | None:
    """Return the diagram keyword, skipping frontmatter, %% directives, comments."""
    lines = body.splitlines()
    index = 0
    if index < len(lines) and lines[index].strip() == "---":
        index += 1
        while index < len(lines) and lines[index].strip() != "---":
            index += 1
        index += 1
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("%%"):
            index += 1
            continue
        match = MERMAID_START_RE.match(stripped)
        return match.group(0) if match else None
    return None


def substantial_snippet(fence: Fence) -> bool:
    lines = [line for line in fence.body.splitlines() if line.strip()]
    return len(lines) >= MIN_SNIPPET_LINES or len(fence.body.strip()) >= MIN_SNIPPET_CHARS


def rationale_section(prose: str) -> str | None:
    """Return the Structure rationale section text, or None when absent."""
    lines = prose.splitlines()
    for index, line in enumerate(lines):
        heading = re.match(r"^(#{1,6})\s+.*structure rationale", line, re.I)
        inline = re.match(r"^\s*(?:[-*]\s+)?\**structure rationale\**\s*:", line, re.I)
        if not heading and not inline:
            continue
        level = len(heading.group(1)) if heading else 7
        body = [line]
        for next_line in lines[index + 1 :]:
            next_heading = re.match(r"^(#{1,6})\s", next_line)
            if next_heading and len(next_heading.group(1)) <= level:
                break
            body.append(next_line)
        return "\n".join(body)
    return None


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


def stem(token: str) -> str:
    """Suffix-strip so summary/summarization or process/processes co-match."""
    token = token.lower()
    for suffix in ("ization", "isation", "ation", "ings", "ing", "ies", "es", "s", "y"):
        if not token.endswith(suffix) or len(token) - len(suffix) < 3:
            continue
        if suffix == "es" and not token[: -2].endswith(("s", "x", "z", "ch", "sh")):
            continue  # templates -> template (via "s"), but processes -> process
        return token[: -len(suffix)]
    return token


def split_ident(raw: str) -> list[str]:
    """Split camelCase/snake_case/kebab-case into lowercase word tokens."""
    parts: list[str] = []
    for chunk in re.split(r"[\s_./:-]+", raw.strip()):
        parts.extend(WORD_RE.findall(CAMEL_RE.sub(" ", chunk)))
    return [part.lower() for part in parts if part]


def line_stems(line: str) -> list[tuple[str, int]]:
    """Stemmed tokens of a prose line with ORIGINAL-line character offsets.

    camelCase words are split in place (offsets stay valid) rather than via a
    substituted copy, so downstream slicing of the original line is exact.
    """
    tokens: list[tuple[str, int]] = []
    for match in WORD_RE.finditer(line):
        position = match.start()
        for part in CAMEL_RE.split(match.group(0)):
            tokens.append((stem(part), position))
            position += len(part)
    return tokens


def code_spans(line: str) -> list[tuple[int, int]]:
    return [match.span(1) for match in INLINE_CODE_RE.finditer(line)]


def headings_of(prose: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for number, line in enumerate(prose.splitlines(), 1):
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            found.append((number, re.sub(r"[`*~]", "", match.group(1))))
    return found


def concept_grams(tokens: list[str], sizes: tuple[int, ...] = (2, 3)) -> set[tuple[str, ...]]:
    """Contiguous stopword-free n-grams (stemmed) from a token list."""
    grams: set[tuple[str, ...]] = set()
    for size in sizes:
        for index in range(len(tokens) - size + 1):
            window = tokens[index : index + size]
            if any(token in STOPWORDS or len(token) < 3 for token in window):
                continue
            grams.add(tuple(stem(token) for token in window))
    return grams


def numbered_sort_key(path: Path) -> tuple[int, str]:
    match = NUMBERED_RE.match(path.stem)
    number = re.match(r"\d+", match.group(1)).group(0) if match else "0"
    return int(number), match.group(1) if match else ""


@dataclass
class Occurrence:
    file: Path
    order: int          # position in the numbered reading order; -1 for fixed files
    line_no: int
    is_home: bool       # heading, glossary-style table row, gloss, or copula definition
    is_bare: bool       # plain use: no gloss, no same-line forward guide link
    in_code: bool       # match sits inside an inline `code` span
    surface: str        # the text as it actually appears on the line


def classify_use(line: str, stems_line: list[tuple[str, int]], start_index: int,
                 size: int, order: int,
                 file_orders: dict[str, int]) -> tuple[bool, bool]:
    """Return (is_home, is_bare) for one concept occurrence on one line."""
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return True, False
    end_token = start_index + size - 1
    end_char = stems_line[end_token][1] + 1
    while end_char < len(line) and (line[end_char].isalnum() or line[end_char] in "_-"):
        end_char += 1
    tail = line[end_char:]
    # Glossary-style table row: concept inside the first cell.
    if stripped.startswith("|"):
        first_cell_end = line.find("|", line.find("|") + 1)
        if first_cell_end > 0 and stems_line[start_index][1] < first_cell_end:
            return True, False
    # Copula within a few tokens and no intervening punctuation: "Background
    # bash processes are tracked" defines; "compaction, branch summary, bash,
    # and Agent are signaled" is a list and does not.
    copula_zone = re.split(r"[,;|/()]|\b(?:and|or)\b", line[end_char:], maxsplit=1)[0]
    raw_following = [w.lower() for w in WORD_RE.findall(copula_zone)[:COPULA_TOKEN_WINDOW]]
    if COPULAS & set(raw_following) or "refers" in raw_following or "means" in raw_following:
        return True, False
    # Parenthetical gloss or em-dash apposition right after the use.
    window = tail[:GLOSS_WINDOW_CHARS]
    paren = re.match(r"\s*[,;]?\s*\(([^)]{8,})\)", window)
    dash = re.match(r"\s*(?:—|--)\s*\S", window)
    colon = re.match(r"\s*:\s+\S", window) if stripped.startswith(("-", "*", "|")) else None
    if paren or dash or colon:
        return True, False
    # Same-line link to a later guide file makes the pointer optional: not bare.
    for destination in inline_links(line):
        name = Path(destination.split("#")[0]).name
        target_order = file_orders.get(name)
        if target_order is not None and target_order > order >= 0:
            return False, False
    return False, True


def self_containment_findings(
    numbered: list[Path], prose_texts: dict[Path, str], fence_bodies: dict[Path, str],
    all_docs: list[Path], waivers: dict[tuple[str, ...], str],
) -> tuple[list[str], list[str], int]:
    """Cumulative-ledger inward pass: orphans and strict forward gaps."""
    ordered = sorted(numbered, key=numbered_sort_key)
    order_of = {doc: index for index, doc in enumerate(ordered)}
    file_orders = {doc.name: index for index, doc in enumerate(ordered)}

    # Concept candidates: heading n-grams (home = that file) + multi-word
    # code identifiers seen anywhere in the guide (inline spans and fences).
    display: dict[tuple[str, ...], str] = {}
    heading_home: dict[tuple[str, ...], int] = {}
    for doc in ordered:
        for _, title in headings_of(prose_texts[doc]):
            for gram in concept_grams(split_ident(title)):
                display.setdefault(gram, " ".join(gram))
                order = order_of[doc]
                if gram not in heading_home or order < heading_home[gram]:
                    heading_home[gram] = order
    # Identifier concepts come from code contexts only (inline spans and fenced
    # snippets), never from plain prose: hyphenated prose compounds are not
    # identifiers and would flood the ledger with false orphans.
    ident_concepts: set[tuple[str, ...]] = set()
    code_evidence: set[tuple[str, ...]] = set()
    for doc in all_docs:
        for source in (
            INLINE_CODE_RE.findall(prose_texts[doc]),
            IDENT_RE.findall(fence_bodies.get(doc, "")),
        ):
            for raw in source:
                tokens = split_ident(raw)
                if not tokens or any(token in STOPWORDS for token in tokens):
                    continue
                stems = tuple(stem(token) for token in tokens)
                # Sub-grams count as code-form evidence (BranchSummaryEntry
                # vouches for "branch summary") without becoming concepts.
                for size in (2, 3):
                    for index in range(len(stems) - size + 1):
                        code_evidence.add(stems[index : index + size])
                if not 2 <= len(tokens) <= 4 or max(len(t) for t in tokens) < 3:
                    continue
                ident_concepts.add(stems)
                display.setdefault(stems, raw)
    concepts = set(heading_home) | ident_concepts

    # Discovery pre-pass: a plain-prose n-gram sitting at a definition-shaped
    # position (copula or parenthetical gloss) is a concept even when it never
    # appears as a heading or an identifier — "Background bash processes are
    # tracked..." anchors "background bash". Definition sites seed the ledger;
    # earlier bare uses then flag naturally.
    for doc in ordered:
        for line in prose_texts[doc].splitlines():
            if line.lstrip().startswith(("#", "|")):
                continue  # headings and tables have their own home rules
            stems_line = line_stems(line)
            spans = code_spans(line)
            # Definition style is line-initial ("Background bash processes are
            # tracked..."): only the line's opening n-gram can seed a concept.
            # Mid-sentence copulas describe; they do not define.
            for size in (2, 3):
                if len(stems_line) < size:
                    continue
                window = stems_line[:size]
                if any(token in STOPWORDS or len(token) < 3 for token, _ in window):
                    continue
                if any(start <= window[0][1] < end for start, end in spans):
                    continue
                is_home, _ = classify_use(
                    line, stems_line, 0, size, order_of[doc], file_orders
                )
                if is_home:
                    gram = tuple(token for token, _ in window)
                    concepts.add(gram)
                    display.setdefault(gram, " ".join(gram))

    # Index prose lines once; then match concepts as contiguous stem runs.
    by_first_stem: dict[str, set[tuple[str, ...]]] = {}
    for gram in concepts:
        by_first_stem.setdefault(gram[0], set()).add(gram)
    occurrences: dict[tuple[str, ...], list[Occurrence]] = {}
    for doc in all_docs:
        order = order_of.get(doc, -1)
        for line_no, line in enumerate(prose_texts[doc].splitlines(), 1):
            stems_line = line_stems(line)
            spans = code_spans(line)
            for index, (token, offset) in enumerate(stems_line):
                for gram in by_first_stem.get(token, ()):
                    size = len(gram)
                    if tuple(t for t, _ in stems_line[index : index + size]) != gram:
                        continue
                    is_home, is_bare = classify_use(
                        line, stems_line, index, size, order, file_orders
                    )
                    in_code = any(start <= offset < end for start, end in spans)
                    last = stems_line[index + size - 1][1]
                    tail_end = last
                    while tail_end < len(line) and (
                        line[tail_end].isalnum() or line[tail_end] in "_-"
                    ):
                        tail_end += 1
                    occurrences.setdefault(gram, []).append(
                        Occurrence(doc, order, line_no, is_home, is_bare,
                                   in_code, line[offset:tail_end])
                    )

    errors: list[str] = []
    warnings: list[str] = []
    for gram, uses in sorted(occurrences.items(), key=lambda item: display[item[0]].lower()):
        if gram in waivers:
            continue
        plain = [use for use in uses if not use.in_code]
        name = next((use.surface for use in plain), display[gram])
        home_orders = [use.order for use in uses if use.is_home and use.order >= 0]
        # Only the README front-loads: a first-cell row in a coverage appendix
        # is back-matter and cannot introduce a term to a linear reader.
        fixed_home = any(
            use.is_home and use.order < 0 and use.file.name.lower() == "readme.md"
            for use in uses
        )
        if gram in heading_home:
            home_orders.append(heading_home[gram])
        # Only plain-prose usage marks a term the reader must understand;
        # backtick-only symbols are code references, not concepts.
        plain_files = {
            use.file.name for use in plain
            if not use.is_home and use.order >= 0
        }
        if not home_orders and not fixed_home:
            if gram in ident_concepts and len(plain_files) >= ORPHAN_MIN_FILES:
                # Advisory by design: no token heuristic can tell a repo term of
                # art from ordinary developer vocabulary ("base URL"). The
                # critic and the authoring pass disposition this ledger; the
                # deterministic gate would false-positive on real guides.
                warnings.append(
                    f"self-containment: orphan concept `{name}`: used in plain "
                    f"prose in {len(plain_files)} files "
                    f"({', '.join(sorted(plain_files))}) but never defined, "
                    "glossed, or given a home heading anywhere in the guide"
                )
            continue
        if fixed_home:
            continue  # defined in README or an appendix: introduced up front
        home = min(home_orders)
        bare = [
            use for use in plain
            if use.is_bare and 0 < use.order < home
        ]
        if not bare:
            continue
        first = min(bare, key=lambda use: (use.order, use.line_no))
        distance = home - first.order
        strong = gram in ident_concepts or gram in code_evidence
        priority = "strong candidate" if strong and distance >= FORWARD_GAP_MIN_DISTANCE \
            else "weak candidate"
        warnings.append(
            f"self-containment: forward gap ({priority}): `{name}` is used in "
            f"{first.file.name}:{first.line_no} with no inline gloss or forward "
            f"link, but its home is {distance} file(s) later "
            f"({sorted(numbered, key=numbered_sort_key)[home].name}); add a same-"
            "sentence gloss or link at first use, or disposition it in the "
            "Self-containment review"
        )
    return errors, warnings, len(concepts)


def parse_waivers(section: str) -> tuple[dict[tuple[str, ...], str], list[str]]:
    """Waivers must name the term, quote the gloss, and justify — or be rejected."""
    waivers: dict[tuple[str, ...], str] = {}
    errors: list[str] = []
    for line in section.splitlines():
        match = WAIVER_RE.match(line)
        if not match:
            continue
        term, remainder = match.group(1), match.group(2).strip()
        quoted = re.search(r"[\"“][^\"”]{8,}[\"”]", remainder)
        bare = re.fullmatch(r"[-\s]*(?:n/?a|none|todo|tbd)?[-\s.]*", remainder, re.I)
        if bare or not quoted or len(remainder) < MIN_WAIVER_SUBSTANCE:
            errors.append(
                f"waiver for `{term}` lacks substance: quote the inline gloss and "
                "state the reason (bare or unquoted waivers are rejected)"
            )
            continue
        waivers[tuple(stem(token) for token in split_ident(term))] = term
    return waivers, errors


def section_text(prose: str, title: str) -> str | None:
    lines = prose.splitlines()
    for index, line in enumerate(lines):
        heading = re.match(rf"^(#{{1,6}})\s+.*{title}", line, re.I)
        if not heading:
            continue
        level = len(heading.group(1))
        body = [line]
        for next_line in lines[index + 1 :]:
            next_heading = re.match(r"^(#{1,6})\s", next_line)
            if next_heading and len(next_heading.group(1)) <= level:
                break
            body.append(next_line)
        return "\n".join(body)
    return None


def count_lines(path: Path) -> tuple[int, int, int]:
    """(all files, code files, non-test code files) line counts for a path."""
    files = [path] if path.is_file() else [
        candidate for candidate in path.rglob("*")
        if candidate.is_file() and not any(part in SCAN_EXCLUDE_DIRS for part in candidate.parts)
    ]
    totals = [0, 0, 0]
    for candidate in files:
        try:
            lines = sum(1 for _ in candidate.open(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        totals[0] += lines
        if candidate.suffix.lower() in CODE_EXTS:
            totals[1] += lines
            if not TEST_PATH_RE.search(str(candidate)):
                totals[2] += lines
    return totals[0], totals[1], totals[2]


def resolve_repo_candidates(repo: Path, raw: str) -> list[Path]:
    """All plausible targets for a code-map path (code maps abbreviate:
    `deploy/` may mean `src/deploy/`). LOC passes if ANY candidate matches."""
    cleaned = raw.strip().strip("`").rstrip("/")
    if not cleaned:
        return []
    candidates: list[Path] = []
    direct = repo / cleaned
    if direct.exists():
        candidates.append(direct)
    basename = cleaned.rsplit("/", 1)[-1]
    for found in repo.rglob(basename):
        if any(part in SCAN_EXCLUDE_DIRS for part in found.parts):
            continue
        if found not in candidates:
            candidates.append(found)
        if len(candidates) >= 8:
            break
    return candidates


def outward_findings(
    repo: Path, guide: Path, texts: dict[Path, str], loc_tolerance: float,
) -> tuple[list[str], list[str]]:
    """Coverage-accuracy nit-catchers: cited LOC sanity and pointer accuracy."""
    errors: list[str] = []
    warnings: list[str] = []
    for appendix_name in REQUIRED_FILES:
        appendix = guide / appendix_name
        if appendix not in texts:
            continue
        for line in texts[appendix].splitlines():
            stripped = line.strip()
            if not stripped.startswith("|") or set(stripped) <= {"|", "-", " ", ":"}:
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            # Paths come from the FIRST path-bearing cell only: later cells are
            # descriptions that may name helper files without mapping them.
            paths: list[str] = []
            for cell in cells:
                found = [
                    token for token in INLINE_CODE_RE.findall(cell)
                    if PATH_CELL_RE.match(token)
                ]
                if found:
                    paths = found
                    break
            links = [
                destination for cell in cells for destination in inline_links(cell)
                if destination.split("#")[0].endswith(".md")
            ]
            if not paths:
                continue
            loc_cells = [match for cell in cells if (match := LOC_CELL_RE.match(cell))]
            if len(paths) == 1 and len(loc_cells) == 1:
                claimed = int(loc_cells[0].group(1).replace(",", ""))
                if loc_cells[0].group(2):
                    claimed *= 1000
                candidates = resolve_repo_candidates(repo, paths[0])
                if claimed >= LOC_MIN_CLAIM and candidates:
                    slack = loc_tolerance * (2 if loc_cells[0].group(2) else 1)
                    all_counts = [count_lines(candidate) for candidate in candidates]
                    if not any(
                        count and abs(count - claimed) <= slack * claimed
                        for counts in all_counts for count in counts
                    ):
                        best = all_counts[0]
                        errors.append(
                            f"{appendix_name}: cited line count {loc_cells[0].group(0)} "
                            f"for `{paths[0]}` does not match source "
                            f"(all={best[0]}, code={best[1]}, non-test code={best[2]}; "
                            f"{len(candidates)} candidate path(s) tried)"
                        )
            if appendix_name != "appendix-code-map.md":
                continue  # pointer accuracy applies to the code map only
            for raw_path in paths:
                target_names = {
                    Path(destination.split("#")[0]).name for destination in links
                }
                targets = [guide / name for name in sorted(target_names)
                           if (guide / name) in texts]
                if not targets:
                    continue
                token = Path(raw_path.rstrip("/")).name
                token = token.rsplit(".", 1)[0] if "." in token else token
                if len(token) < 3:
                    continue
                pattern = re.compile(rf"\b{re.escape(token)}", re.I)
                stem_gram = tuple(stem(part) for part in split_ident(token))
                compressed_token = re.sub(r"[\s_-]", "", token.lower())
                mentioned = False
                for target in targets:
                    if pattern.search(texts[target]):
                        mentioned = True
                        break
                    # "ratelimit/" is mentioned as "rate limiting": compare with
                    # separators stripped on both sides.
                    compressed_text = re.sub(r"[\s_-]", "", texts[target].lower())
                    if compressed_token and compressed_token in compressed_text:
                        mentioned = True
                        break
                    target_stems = [
                        token_stem for token_stem, _ in line_stems(texts[target])
                    ]
                    for index in range(len(target_stems) - len(stem_gram) + 1):
                        if tuple(target_stems[index : index + len(stem_gram)]) == stem_gram:
                            mentioned = True
                            break
                    if mentioned:
                        break
                if not mentioned:
                    errors.append(
                        f"{appendix_name}: maps `{raw_path}` to "
                        f"{', '.join(sorted(target_names))} but no linked file "
                        "mentions it; repoint the row or cover the subsystem"
                    )
    return errors, warnings


def cli_completeness_warnings(repo: Path, guide_text: str) -> list[str]:
    """Advisory: CLI subcommands in source that the guide never names."""
    names: set[str] = set()
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SCAN_EXCLUDE_DIRS]
        for file_name in files:
            path = Path(root) / file_name
            if path.suffix.lower() not in CODE_EXTS:
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pattern in CLI_CMD_RES:
                names.update(match.group(1) for match in pattern.finditer(content))
    missing = sorted(
        name for name in names
        if not re.search(rf"\b{re.escape(name)}\b", guide_text)
    )
    if missing:
        return [
            "CLI subcommands found in source but never mentioned in the guide "
            f"(advisory): {', '.join(missing[:15])}"
        ]
    return []


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
    for required in REQUIRED_FILES:
        if not (guide / required).exists():
            errors.append(f"guide is missing required file {required}")

    numbered = [d for d in markdown if NUMBERED_RE.match(d.stem)]
    numbered_set = set(numbered)
    generic = sorted(
        d.name for d in numbered if NUMBERED_RE.match(d.stem).group(2) in GENERIC_STEMS
    )
    if numbered and len(generic) >= max(3, (len(numbered) + 1) // 2):
        errors.append(
            "file plan is dominated by generic template names instead of this "
            "repository's subsystems: " + ", ".join(generic)
        )

    texts: dict[Path, str] = {}
    prose_texts: dict[Path, str] = {}
    fence_bodies: dict[Path, str] = {}
    diagrams = snippets = local_link_count = 0
    mermaid_seen: set[str] = set()
    sequence_found = False

    for document in markdown:
        text = document.read_text(encoding="utf-8")
        prose, fences, balanced = split_fences(text)
        texts[document], prose_texts[document] = text, prose
        fence_bodies[document] = "\n".join(fence.body for fence in fences)
        if not balanced:
            errors.append(f"{document.name}: unbalanced fenced code block")
        placeholders = sorted(set(PLACEHOLDER_RE.findall(prose)))
        if placeholders:
            errors.append(f"{document.name}: contains prose placeholders: {placeholders}")
        if document in numbered_set and len(prose.split()) < MIN_NUMBERED_WORDS:
            errors.append(
                f"{document.name}: under {MIN_NUMBERED_WORDS} words of prose; looks like a stub"
            )

        prose_lines = prose.splitlines()
        for fence in fences:
            if fence.language == "mermaid":
                kind = mermaid_kind(fence.body)
                body_lines = [line for line in fence.body.splitlines() if line.strip()]
                key = normalized_source(fence.body)
                if kind and len(body_lines) >= MIN_DIAGRAM_LINES and key not in mermaid_seen:
                    mermaid_seen.add(key)
                    diagrams += 1
                    if kind.startswith("sequenceDiagram"):
                        sequence_found = True
        snippets += sum(
            f.language not in NON_SOURCE_LANGS
            and substantial_snippet(f)
            and snippet_has_source_link(document, prose_lines, f, repo)
            for f in fences
        )

        for destination in local_links(prose):
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
    elif not sequence_found:
        warnings.append(
            "no sequenceDiagram found; the end-to-end runtime sequence diagram may be missing"
        )
    if snippets < args.min_source_snippets:
        errors.append(
            f"found {snippets} non-empty source snippets with nearby source links; "
            f"require {args.min_source_snippets}"
        )

    index = texts.get(readme, "")
    if readme.exists():
        section = rationale_section(prose_texts[readme])
        if section is None:
            errors.append("README.md does not declare structure rationale")
        else:
            for document in numbered:
                if document.stem not in section and document.name not in section:
                    errors.append(f"structure rationale does not mention {document.name}")

        indexed: set[Path] = set()
        for destination in local_links(prose_texts[readme]):
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

    coverage = guide / "appendix-coverage-and-evidence.md"
    waivers: dict[tuple[str, ...], str] = {}
    if coverage.exists():
        coverage_prose = prose_texts.get(coverage, "")
        if not re.search(r"^#{1,6}\s+Structure-fit review\b", coverage_prose, re.I | re.M):
            errors.append(
                "appendix-coverage-and-evidence.md has no `Structure-fit review` section"
            )
        sc_section = section_text(coverage_prose, "self-containment review")
        if sc_section is None:
            errors.append(
                "appendix-coverage-and-evidence.md has no `Self-containment review` "
                "section (critic's inward verdict plus any waivers)"
            )
        else:
            if len(sc_section.split()) < SC_SECTION_MIN_WORDS:
                errors.append(
                    "`Self-containment review` section is a stub; record the critic's "
                    "verdict on forward dependencies, thin definitions, and traps"
                )
            waivers, waiver_errors = parse_waivers(sc_section)
            errors.extend(waiver_errors)

    concept_count = 0
    if numbered:
        inward_errors, inward_warnings, concept_count = self_containment_findings(
            numbered, prose_texts, fence_bodies, markdown, waivers
        )
        errors.extend(inward_errors)
        warnings.extend(inward_warnings)
    outward_errors, outward_warnings = outward_findings(
        repo, guide, texts, args.loc_tolerance
    )
    errors.extend(outward_errors)
    warnings.extend(outward_warnings)
    if not args.skip_cli_scan:
        warnings.extend(
            cli_completeness_warnings(repo, "\n".join(texts.values()))
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

    return report(
        errors, warnings, len(markdown), local_link_count, diagrams, snippets,
        concept_count,
    )


def report(
    errors: list[str], warnings: list[str], markdown_count: int,
    link_count: int, diagram_count: int, snippet_count: int,
    concept_count: int = 0,
) -> int:
    print(
        f"files={markdown_count} local_links={link_count} diagrams={diagram_count} "
        f"source_snippets={snippet_count} tracked_concepts={concept_count}"
    )
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
