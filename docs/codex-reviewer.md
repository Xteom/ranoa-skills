# codex-reviewer: design notes and codex CLI gotchas

Notes behind [`agents/codex-reviewer.md`](../agents/codex-reviewer.md), learned by
testing against `codex-cli 0.144.5` (2026-07-29). If the agent misbehaves after a
codex upgrade, re-verify these first.

## Design

- The agent is a **thin relay**, not a reviewer: the value is that the verdict
  comes from a different model (OpenAI Codex), with different blind spots than
  Claude. It must return codex's output verbatim — never softened, filtered, or
  merged with its own opinion.
- `model: haiku` for the wrapper is enough: its job is mechanical (gather
  context, run a CLI, relay). Verified end-to-end with a haiku subagent — it
  followed the procedure and relayed a high-quality verdict. Bump to sonnet only
  if the prompts it assembles for codex turn out too thin on vague requests.
- Sandbox stays `read-only`: a reviewer must not modify the workspace. Use
  `workspace-write` only if you explicitly want codex to apply fixes.

## codex CLI facts (verified by running, not from docs)

| Fact | Consequence |
|---|---|
| Raw stdout is a noisy event stream (~330 lines around a 9-line verdict), and codex may print the verdict twice | Always capture with `-o/--output-last-message <file>`; never parse stdout, never use `> out.txt 2>&1` |
| `codex exec review` is a purpose-built repo review mode with `--uncommitted`, `--base <branch>`, `--commit <sha>` | Prefer it over hand-assembling diffs when reviewing a git repo |
| Scope flags (`--uncommitted` / `--base` / `--commit`) **cannot** be combined with a custom instructions prompt | Pass either a scope flag or instructions, not both (errors otherwise) |
| `review` supports `-o` but **not** `-C` | `cd` into the repo before `codex exec review ...` |
| `codex exec` refuses to run outside a git repo by default | Add `--skip-git-repo-check` for ad-hoc (Mode B) runs from scratch dirs |
| `-` reads the prompt from stdin | Pipe long prompts from a file: avoids shell-quoting breakage and arg-length limits on big diffs |
| Codex's sandbox blocks `/tmp` writes; test suites it runs during a review can fail with "No usable temporary directory" | Expect occasional sandbox-artifact noise in review verdicts — not a real failure in the reviewed repo |

## Artifact hygiene

Write the prompt and verdict files to a fresh temp dir (`mktemp -d`) or the
harness scratchpad — **never inside the reviewed repo**. Fixed names like
`prompt.md` could overwrite real files and leave untracked artifacts containing
copied source text. (Found by codex itself while reviewing an earlier version of
this agent.)
