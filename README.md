# ranoa-skills

A Claude Code plugin with skills and agents I use day to day.

## What's inside

| Component | Type | What it does |
|---|---|---|
| `repo-expert-onboarding` | Skill | Generates an expert-level, source-grounded onboarding guide for any repository — architecture, diagrams, coverage-matrix-driven structure, validated output. |
| `codex-reviewer` | Agent | A cross-model second opinion. Relays a review request to the OpenAI `codex` CLI and returns its verdict verbatim — a genuinely different model's point of view, not another Claude persona. Requires `codex` on your PATH. |

## Install

```
/plugin marketplace add Xteom/ranoa-skills
/plugin install ranoa@ranoa-skills
```

Then restart Claude Code. The skill is invocable as `/ranoa:repo-expert-onboarding`, and `codex-reviewer` appears as an agent type for the Agent tool.

## Why a cross-model reviewer?

A subagent of the same model shares its blind spots. `codex-reviewer` exists so Claude can ask a *different* model to adversarially review a diff or design and surface disagreements instead of smoothing them over.

## License

MIT — see [LICENSE](LICENSE).
