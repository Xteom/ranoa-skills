# Codex agent dispatch reliability — findings and fix design

Date: 2026-08-28. Status: **findings + design. One file changed, outside this
repo** (`~/.claude/agents/codex-reviewer.md`, backup at `.bak`); F4 below
supersedes part of that edit and it should not be considered final. Question
posed: why does Claude sometimes not invoke the Codex agent, and how do we make
invocation reliable?

Answer: the reported symptom is real but **misnamed**. In the session that
prompted this, dispatch succeeded. What failed was that the dispatched agent had
no procedure covering the task and no context to improvise one. Enforcement
mechanisms fix the invocation problem; they do nothing for the failure that
actually occurred.

Companion research: `docs/2026-08-26-external-llm-cross-review-research.md`
probed four external LLM CLIs for the onboarding skill. Its F1 (containment)
independently governs F4 here. **That file is untracked as of this commit** — the
cross-reference dangles until it is committed.

## Method

Direct inspection, not reasoning from description:

1. Read `~/.claude/agents/codex-reviewer.md` in full.
2. Verified every flag claim against `codex exec --help` on the installed binary
   (`codex-cli 0.149.0`).
3. Read `~/.codex/config.toml` for trust and model state.
4. Read `~/.claude/settings.json` and the existing `usage-guard.sh` hook for the
   in-use hook idiom.
5. Loaded the `update-config` skill for the authoritative settings schema.

## Findings

### F1 — the "Claude won't invoke it" complaint misdiagnoses a context failure (HIGH)

The triggering task asked the agent to inspect several cloned harnesses under
`~/Documents/cura/research` and explicitly said *"actually inspect the cloned
harnesses — do not judge from names alone."* The agent launched. It could not
comply.

A subagent starts with **no conversation context**. It received that instruction
as text, but nothing conveyed that `~/Documents/cura/research` was the root or
that `hermes`, `pi`, `orca` were directories under it — unless the dispatching
Claude enumerated all of it. It did not, because from the dispatcher's side
delegating *is* the act of not enumerating.

**Consequence:** this is structural to the relay-agent design, and no amount of
dispatch enforcement addresses it. A perfectly-dispatched agent still starts
blind. Fixing invocation and fixing capability are two separate work items, and
only the second was the actual failure.

### F2 — no mode covered filesystem investigation; `-C` appeared nowhere (CRITICAL)

The definition offered exactly two procedures. Mode A ran `codex exec review`
against a git diff — inapplicable, there was no diff. Mode B built a
self-contained prompt and piped it to:

```
codex exec -s read-only --skip-git-repo-check -o "$OUT/codex-verdict.txt" - < "$OUT/prompt.md"
```

No `-C`, no working root, anywhere in the file. Verified against the installed
binary, `-C, --cd <DIR>` exists and is exactly the missing piece:

```
-C, --cd <DIR>    Tell the agent to use the specified directory as its working root
```

Without it codex receives a text blob and no filesystem. So the agent had two
bad options: follow its instructions faithfully and hand codex a prompt it could
not act on, or improvise an invocation the definition never describes.

**Consequence:** a third mode is required — investigate a directory tree, `-C`
mandatory — plus a step that resolves the working root *before* mode selection,
and a sanity check that a verdict claiming to have inspected files actually
cites one.

### F3 — `model: haiku` placed the judgment call on the least capable model (MEDIUM)

The frontmatter pinned `model: haiku` and the body said *"You do not review
anything yourself."* Both are defensible for a pure relay. Together they made the
F2 improvisation maximally unlikely: the cheapest model, explicitly instructed
not to exercise judgment, was the only thing positioned to notice that no mode
fit.

**Consequence:** the model tier is downstream of the architecture, not a
standalone fix. Under a **relay-only** design where the caller pre-builds the
full command, haiku is genuinely sufficient. Under the **standalone-agent**
design where the agent designs the invocation, it is not. Choosing the tier
before choosing the architecture is the error.

### F4 — `-s read-only` is not enforced on this machine (CRITICAL)

Both the original definition and the 2026-08-28 rewrite state *"Keep the sandbox
`read-only` — a reviewer must not modify the workspace."* On this host that is a
safety claim that does not hold. `~/.codex/config.toml`:

```toml
[projects."/home/xteom"]
trust_level = "trusted"
```

The entry covers the entire home directory, so it subsumes
`~/Documents/cura/research`, this repo, and every other target a review would
plausibly be pointed at. The companion doc demonstrated the breach empirically
rather than inferring it (`2026-08-26-external-llm-cross-review-research.md`,
F1): a `-s read-only` run was instructed to create a file and reported *"The
write succeeded."* Re-running with `--ignore-user-config` produced the correct
refusal.

**Consequence:** `--ignore-user-config` is mandatory in every invocation, not
optional hardening — and it must be paired with `--ignore-rules` so project
`.rules` files cannot re-open what the flag closed. The rewritten agent file is
**not correct as committed** and needs this before use. A reviewer agent that
claims containment it has not verified is worse than one that claims nothing.

### F5 — the codex default model drifted within two days (LOW, confirms a prediction)

The companion doc recorded codex serving `gpt-5.6-sol` on 2026-08-26 and warned
the default *"will drift silently."* Today `~/.codex/config.toml` reads:

```toml
model = "gpt-5.6-luna"
```

**Consequence:** confirmed in 48 hours. Any recorded cross-model verdict must
pin `-m` explicitly and capture the model in its provenance line, or the verdict
is unattributable after the fact.

## Fix design

### The mechanisms differ on two axes; only one axis addressed the real failure

| Mechanism | Fires when | Context available | Isolates codex output |
|---|---|---|---|
| Agent (`codex-reviewer.md`) | Claude matches `description` | **none** — starts blank | yes |
| Skill (`/codex`) | slash command, or description match | **full conversation** | no — runs in main context |
| `CLAUDE.md` rule | always loaded | full | n/a |
| `UserPromptSubmit` hook | deterministic regex on the prompt | n/a — injects text | n/a |

F1 lives in the *context* column. Only the skill row changes it.

### Recommended: skill as front door, agent as execution sandbox

Not either/or. The split follows the failure:

- **`~/.claude/skills/codex/SKILL.md`** — owns the judgment. Resolves the `-C`
  root from the conversation, selects the mode, writes a prompt file naming
  concrete paths. Runs where the context already exists.
- **`codex-reviewer` agent** — receives a fully-formed command to *execute*, not
  a task to design. It becomes the thin relay it always claimed to be, codex's
  noisy event stream stays out of the main context via `-o`, and F3 resolves in
  favor of keeping haiku.

This also gives a deterministic invocation path (`/codex`) that involves no
description matching at all — which is the whole of the "always invoke it"
request.

### Local enforcement leverage worth noting

`superpowers@claude-plugins-official` is enabled in `~/.claude/settings.json`,
and its `using-superpowers` skill is injected at SessionStart with an explicit
anti-rationalization mandate: *"IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE
A CHOICE. YOU MUST USE IT."* That mandate is scoped to **skills**; there is no
agent equivalent. Moving the entry point to a skill inherits enforcement
machinery already installed and already firing every session, rather than adding
a new mechanism to do the same job.

### Enforcement ranking for the prose path ("have codex look at this")

1. `UserPromptSubmit` hook — deterministic injection
2. skill under the superpowers mandate — strong, already installed
3. `CLAUDE.md` rule — user instruction, outranks default behavior
4. agent `description` — weakest; the status quo

**Recommendation: defer the hook.** Build the skill, use it, add the hook only if
prose requests are still observed slipping. Adding it now optimizes a failure
that the skill may remove.

## `UserPromptSubmit` hook contract — verified vs. not

Registration lives in `~/.claude/settings.json` as a sibling of the existing
`PostToolBatch` entry; the script alongside `usage-guard.sh` and `statusline.sh`,
addressed as `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/…` so the `~/.claude-cura`
split keeps working.

**Confirmed against the settings schema:**

- `UserPromptSubmit` is a valid event; `matcher` is optional (only `hooks` is
  required), so omitting it is correct rather than a shortcut.
- Output shape `hookSpecificOutput.{hookEventName, additionalContext}` — the same
  contract `usage-guard.sh:165` already uses, with the event name swapped.
- `decision: "block"` + `reason` is valid for this event. This is the documented
  blocking path; the exit-code-2 route is not the one to reach for. Blocking is
  **not recommended** regardless — it fights the user rather than helping.
- `prompt` and `agent` hook types are tool-events-only. On `UserPromptSubmit`
  only `command` is available.

**Not confirmed:** the stdin payload field names for this event. The schema
documents the payload only in its tool-event shape (`tool_name`, `tool_input`,
`tool_response`). Whether the raw user text arrives as `.prompt` is **unverified**
— `usage-guard.sh` does `cat >/dev/null`, so it is no evidence. Resolve with a
self-removing probe before writing any real matcher:

```json
{ "type": "command", "once": true, "command": "cat >> /tmp/ups-payload.json" }
```

## Limits

- **A hook injects text; it cannot force a tool call.** "Deterministic" describes
  the injection, not the dispatch. It is a large reliability gain, not a
  guarantee. Only `/codex` — typed by the user — removes matching entirely.
- **F4 is host-specific.** The `trust_level` entry is this machine's config. The
  finding generalizes as *verify containment, never assume it*; the specific
  breach does not.
- **Nothing here is measured.** F1–F3 are read from source and one session's
  behavior, not from a failure-rate experiment across many dispatches.

## Residuals — not tested

- The skill-plus-agent split has not been built or exercised.
- The `UserPromptSubmit` payload probe has not been run.
- Whether the strengthened `description` alone (`MUST BE USED whenever…`)
  measurably improves dispatch, absent any other mechanism.
- Whether `--ignore-user-config` has side effects on auth, which lives in
  `CODEX_HOME` and is documented as unaffected but was not verified here.

## Appendix: reproduction commands

```sh
# F2 — confirm the working-root flag exists
codex exec --help | grep -A1 '^  -C, --cd'

# F4 — the trust entry that defeats -s read-only
grep -A1 'projects."/home/xteom"\]' ~/.codex/config.toml

# F4 — containment canary; MUST be refused. Without --ignore-user-config
#      on this host it reports success instead.
codex exec -s read-only --ignore-user-config --ignore-rules --ephemeral -C <dir> \
  'Write hello into ./probe_write.txt; report whether it succeeded or was denied.'

# F5 — the drifting default
grep '^model' ~/.codex/config.toml

# Mode C shape the definition was missing
codex exec -C <root-dir> -s read-only --ignore-user-config --ignore-rules \
  --skip-git-repo-check -o "$OUT/codex-verdict.txt" - < "$OUT/prompt.md"
```
