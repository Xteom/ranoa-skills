# Domain Module: CLI Tool / Published Library

Apply this module on either of two independent triggers, which contribute different topic sets. (a) **CLI/TUI surface**: `bin` entries or console-script entry points, TUI frameworks, shell completions or man pages — contributes the command-surface, configuration, TUI, and cross-platform topics. (b) **Published library**: proven publication — no `"private": true` plus a `publishConfig`/registry target, or a publish/release CI job (a build-system stanza or bare `package.json`/`pyproject.toml` in a workspace is workspace membership, not publication) — adds the public-API/SDK, package-layout, release-engineering, and supply-chain topics. A repo matching (a) only must not receive release-engineering or supply-chain matrix rows.

This module contributes topics and questions to the coverage matrix. It never names guide files — the file plan derives from the matrix.

## Required topics

Merge each topic into the coverage matrix. Any of these that is first-class in this repository is a deep-coverage candidate in the coverage matrix; the File Plan in SKILL.md decides file boundaries and counts.

- **Command surface.** Commands, flags, exit codes, stdin/stdout contracts; interactive versus non-interactive versus machine modes (print/JSON/RPC) and how mode selection is resolved.
- **Configuration.** Precedence across defaults, config files, env vars, and flags; hot-reload versus restart per setting group; places where config merging is shallower than its naming claims.
- **TUI.** Rendering model, component inventory, keybindings, terminal-compatibility constraints. A TUI layer that is itself a published package is a first-class subsystem, not a UI footnote.
- **Public API/SDK surface.** What each package exports, what is semver-stable versus internal, and the embedding story for programmatic consumers.
- **Package layout.** Workspace/dependency DAG between packages, and which packages are published versus internal-only.
- **Release engineering.** Versioning, changelogs, publish flow, artifact verification, and the exact gates a release script enforces.
- **Supply-chain controls.** Lockfile policy, lifecycle-script allowlists, install-time behavior, dependency pinning, vendoring. These are usually scattered across build scripts and CI — collect them into one coherent account.
- **Extension loading.** Plugin/extension discovery, the trust model for third-party code, and sandboxing if any.
- **Cross-platform behavior.** Paths, shells, terminals, OS-specific test scripts, CI matrices.

## Investigation questions

- How does the binary decide which mode it is in, and which surfaces exist only in one mode?
- Which packages are published, under what names, and what would a semver-breaking change look like for each?
- What runs at install time (postinstall, lifecycle scripts), and what policy constrains it?
- What does the release process actually verify before publishing?
- Which parts of the public API are re-exports of internals that can drift?
- How is the TUI tested, and what cannot be tested without a real terminal?

## Traps observed in practice

- Supply-chain hardening is a distinctive, security-relevant trait that hides in `preinstall` scripts, CI, and lockfile policy; surface it as one topic instead of scattering mentions.
- The largest single source file is often the interactive mode; flag it as risky-to-modify and map its extension seams.
- Libraries embedded by other repositories have two audiences — contributors and embedders; the guide must serve both or say which it serves.
