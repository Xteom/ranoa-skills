#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_guide.py")

FILLER = (
    "This section explains the subsystem in enough depth to satisfy the stub "
    "check used by the validator. " * 4
)
NAMES = ["01-alpha-engine.md", "02-beta-store.md", "03-gamma-api.md", "04-delta-cli.md"]
APPENDICES = ["appendix-code-map.md", "appendix-coverage-and-evidence.md"]

SNIPPET_A = "def run(limit):\n    total = sum(range(limit))\n    return total"
SNIPPET_B = "def report(value):\n    label = f\"total={value}\"\n    return label"
DIAGRAM_FLOW = "```mermaid\nflowchart LR\n  A --> B\n  B --> C\n```\n"
DIAGRAM_SEQ = "```mermaid\nsequenceDiagram\n  A->>B: call\n  B-->>A: reply\n```\n"


class ValidateGuideTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.guide = self.repo / "guide"
        self.guide.mkdir(parents=True)
        self.source = self.repo / "src.py"
        self.source.write_text(
            "def run(limit):\n"
            "    total = sum(range(limit))\n"
            "    return total\n"
            "\n"
            "def report(value):\n"
            "    label = f\"total={value}\"\n"
            "    return label\n"
            "\n"
            "result = report(run(10))\n",
            encoding="utf-8",
        )
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test")
        self._git("add", "src.py")
        self._git("commit", "-qm", "initial")
        self.commit = self._git("rev-parse", "HEAD").stdout.strip()
        self.branch = self._git("branch", "--show-current").stdout.strip()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args], cwd=self.repo, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=True,
        )

    def _run(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable, str(SCRIPT), "--repo", str(self.repo),
                "--guide", str(self.guide), "--min-files", "5",
                "--min-diagrams", "2", "--min-source-snippets", "2",
                "--require-metadata", "--require-head-match",
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )

    def _metadata(self) -> str:
        return (
            f"Commit: `{self.commit}`\n"
            f"Branch: `{self.branch}`\n"
            "Analyzed: 2026-07-01\n"
            "Working tree before generation: clean\n"
            "Upstream divergence: unknown\n"
        )

    def _index(self, names: list[str]) -> str:
        return "\n## Index\n\n" + "\n".join(f"[{n}]({n})" for n in names + APPENDICES) + "\n"

    def _rationale(self, names: list[str]) -> str:
        lines = "".join(f"- {n}: covers its own surface row.\n" for n in names)
        return f"\n## Structure rationale\n\n{lines}"

    def _evidence(self) -> str:
        return (
            "\n## Evidence\n\n"
            "Source: [run implementation](../src.py#L1-L3)\n"
            f"```python\n{SNIPPET_A}\n```\n"
            "\nSource: [report helper](../src.py#L5-L7)\n"
            f"```python\n{SNIPPET_B}\n```\n"
            + DIAGRAM_FLOW
            + DIAGRAM_SEQ
        )

    def _write_numbered(self, names: list[str], body: str = FILLER) -> None:
        for name in names:
            (self.guide / name).write_text(f"# {name}\n\n{body}\n", encoding="utf-8")

    def _write_appendices(self, with_fit_section: bool = True,
                          with_sc_section: bool = True,
                          code_map_extra: str = "",
                          sc_extra: str = "") -> None:
        (self.guide / "appendix-code-map.md").write_text(
            f"# Code map\n\n{FILLER}\n{code_map_extra}\n", encoding="utf-8"
        )
        fit = (
            "\n## Structure-fit review\n\n"
            "The critic confirmed the plan follows the coverage matrix.\n"
            if with_fit_section
            else ""
        )
        sc = (
            "\n## Self-containment review\n\n"
            "The critic walked the numbered files in reading order and confirmed "
            "each file is understandable given only the README and earlier files; "
            "no thin definitions, wrong-model traps, or two-sense terms were found.\n"
            f"{sc_extra}\n"
            if with_sc_section
            else ""
        )
        (self.guide / "appendix-coverage-and-evidence.md").write_text(
            f"# Coverage and evidence\n{fit}{sc}\n{FILLER}\n", encoding="utf-8"
        )

    def _write_readme(self, names: list[str], rationale_names: list[str] | None = None,
                      index: str | None = None, evidence: str | None = None) -> None:
        (self.guide / "README.md").write_text(
            "# Guide\n\n"
            + self._metadata()
            + (index if index is not None else self._index(names))
            + self._rationale(rationale_names if rationale_names is not None else names)
            + (evidence if evidence is not None else self._evidence()),
            encoding="utf-8",
        )

    def _build_valid(self) -> None:
        self._write_numbered(NAMES)
        self._write_appendices()
        self._write_readme(NAMES)

    def test_valid_guide_passes(self) -> None:
        self._build_valid()
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generic_template_regression_fails(self) -> None:
        generic = [
            "01-big-picture.md", "02-setup-entrypoints-and-configuration.md",
            "03-runtime-flow.md", "04-core-domain-model.md",
        ]
        self._write_numbered(generic)
        self._write_appendices()
        self._write_readme(generic)
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generic template names", result.stdout)

    def test_rationale_must_mention_every_numbered_file(self) -> None:
        self._write_numbered(NAMES)
        self._write_appendices()
        self._write_readme(NAMES, rationale_names=NAMES[:3])
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("structure rationale does not mention 04-delta-cli.md", result.stdout)

    def test_reference_style_index_links_pass(self) -> None:
        self._write_numbered(NAMES)
        self._write_appendices()
        labels = NAMES + APPENDICES
        index = (
            "\n## Index\n\n"
            + "\n".join(f"[{n}][ref{i}]" for i, n in enumerate(labels))
            + "\n\n"
            + "\n".join(f"[ref{i}]: {n}" for i, n in enumerate(labels))
            + "\n"
        )
        self._write_readme(NAMES, index=index)
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("does not link", result.stdout)

    def test_underscore_anchor_and_mermaid_directive_pass(self) -> None:
        self._write_numbered(NAMES[1:])
        (self.guide / NAMES[0]).write_text(
            f"# Alpha engine\n\n## run_agent()\n\n{FILLER}\n", encoding="utf-8"
        )
        (self.guide / NAMES[1]).write_text(
            f"# Beta store\n\nSee [the loop]({NAMES[0]}#run_agent).\n\n{FILLER}\n",
            encoding="utf-8",
        )
        self._write_appendices()
        directive_diagram = (
            "```mermaid\n%%{init: {\"theme\": \"dark\"}}%%\nflowchart LR\n"
            "  A --> B\n  B --> C\n```\n"
        )
        evidence = (
            "\n## Evidence\n\n"
            "Source: [run implementation](../src.py#L1-L3)\n"
            f"```python\n{SNIPPET_A}\n```\n"
            "\nSource: [report helper](../src.py#L5-L7)\n"
            f"```python\n{SNIPPET_B}\n```\n"
            + directive_diagram
            + DIAGRAM_SEQ
        )
        self._write_readme(NAMES, evidence=evidence)
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("missing heading anchor", result.stdout)

    def test_trivial_snippets_and_duplicate_diagrams_rejected(self) -> None:
        self._write_numbered(NAMES)
        self._write_appendices()
        evidence = (
            "\n## Evidence\n\n"
            "Source: [result](../src.py#L9)\n"
            "```python\nresult = report(run(10))\n```\n"
            "\nSource: [result again](../src.py#L9)\n"
            "```python\nresult = report(run(10))\n```\n"
            + DIAGRAM_FLOW
            + DIAGRAM_FLOW
        )
        self._write_readme(NAMES, evidence=evidence)
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source snippets", result.stdout)
        self.assertIn("Mermaid diagrams", result.stdout)

    def test_missing_appendix_and_structure_fit_section(self) -> None:
        self._write_numbered(NAMES)
        self._write_readme(NAMES)
        (self.guide / "appendix-code-map.md").write_text(
            f"# Code map\n\n{FILLER}\n", encoding="utf-8"
        )
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "missing required file appendix-coverage-and-evidence.md", result.stdout
        )

        self._write_appendices(with_fit_section=False)
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Structure-fit review", result.stdout)

        self._write_appendices(with_sc_section=False)
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Self-containment review", result.stdout)

    def test_fake_evidence_and_plain_filenames_do_not_pass(self) -> None:
        self._write_numbered(NAMES, body="Stub.")
        self._write_appendices()
        (self.guide / "README.md").write_text(
            "# Guide\n" + self._metadata()
            + " ".join(NAMES) + "\n"
            + self._rationale(NAMES)
            + "\nSource: [implementation](../src.py)\n"
            + "```python\nnot_in_source()\nstill_not_in_source()\nalso_fake()\n```\n"
            + "```mermaid\nx\n```\n```mermaid\ny\n```\n",
            encoding="utf-8",
        )
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not link", result.stdout)
        self.assertIn("non-empty Mermaid", result.stdout)
        self.assertIn("source snippets", result.stdout)
        self.assertIn("looks like a stub", result.stdout)

    def _write_orphan_files(self, define: bool = False) -> None:
        """`dataFlux` used across three files; defined only when asked."""
        definition = (
            "| `dataFlux` | The per-request effort knob shared by every adapter. |\n"
            if define
            else ""
        )
        (self.guide / NAMES[0]).write_text(
            f"# Alpha engine\n\n| Term | Meaning |\n| --- | --- |\n{definition}\n"
            f"{FILLER}\n```python\nconfig = {{'dataFlux': 3}}\n```\n",
            encoding="utf-8",
        )
        (self.guide / NAMES[1]).write_text(
            f"# Beta store\n\nWrites honor the data flux ceiling.\n\n{FILLER}\n",
            encoding="utf-8",
        )
        (self.guide / NAMES[2]).write_text(
            f"# Gamma api\n\nResponses carry per-data-flux borders.\n\n{FILLER}\n",
            encoding="utf-8",
        )
        (self.guide / NAMES[3]).write_text(
            f"# Delta cli\n\nThe cli prints the data flux value.\n\n{FILLER}\n",
            encoding="utf-8",
        )

    def test_orphan_concept_flagged_as_advisory(self) -> None:
        self._write_orphan_files(define=False)
        self._write_appendices()
        self._write_readme(NAMES)
        result = self._run()
        # Concept-level inward findings are advisory (critic input), not gates.
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("orphan concept", result.stdout)
        self.assertIn("data flux", result.stdout)

    def test_orphan_suppressed_by_glossary_row(self) -> None:
        self._write_orphan_files(define=True)
        self._write_appendices()
        self._write_readme(NAMES)
        result = self._run()
        self.assertNotIn("orphan concept", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def _write_gap_files(self, first_use: str) -> None:
        """Home heading for 'delta batching' lives in file 04; use is in 02."""
        self._write_numbered([NAMES[0], NAMES[2]])
        (self.guide / NAMES[1]).write_text(
            f"# Beta store\n\n{first_use}\n\n{FILLER}\n", encoding="utf-8"
        )
        (self.guide / NAMES[3]).write_text(
            f"# Delta cli\n\n## Delta Batching\n\nDelta batching groups writes into "
            f"one flush and is the cli's core loop.\n\n{FILLER}\n",
            encoding="utf-8",
        )

    def test_forward_gap_flagged_as_advisory(self) -> None:
        self._write_gap_files("The store relies on delta batching for flushes.")
        self._write_appendices()
        self._write_readme(NAMES)
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("forward gap", result.stdout)
        self.assertIn(NAMES[1], result.stdout)

    def test_forward_gap_spared_by_gloss_and_by_link(self) -> None:
        self._write_gap_files(
            "The store relies on delta batching (grouping writes into one flush)."
        )
        self._write_appendices()
        self._write_readme(NAMES)
        result = self._run()
        self.assertNotIn("forward gap", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        self._write_gap_files(
            f"The store relies on delta batching ([04]({NAMES[3]}))."
        )
        result = self._run()
        self.assertNotIn("forward gap", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_waiver_suppresses_gap_but_bare_waiver_rejected(self) -> None:
        self._write_gap_files("The store relies on delta batching for flushes.")
        self._write_appendices(sc_extra=(
            '- Waiver: `delta batching` — glossed upstream as "grouping writes '
            'into one flush"; introduced early on purpose because the store '
            "chapter motivates the batching design.\n"
        ))
        self._write_readme(NAMES)
        result = self._run()
        self.assertNotIn("forward gap", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        self._write_appendices(sc_extra="- Waiver: `delta batching` — n/a\n")
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lacks substance", result.stdout)

    def test_loc_mismatch_flagged_and_accurate_passes(self) -> None:
        module = self.repo / "engine.py"
        module.write_text("\n".join(f"x{i} = {i}" for i in range(120)) + "\n",
                          encoding="utf-8")
        self._write_numbered(NAMES)
        (self.guide / NAMES[0]).write_text(
            f"# Alpha engine\n\nThe engine module drives it.\n\n{FILLER}\n",
            encoding="utf-8",
        )
        row = "| Path | Lines | Files |\n| --- | --- | --- |\n"
        self._write_appendices(code_map_extra=(
            row + f"| `engine.py` | 400 | [01]({NAMES[0]}) |\n"
        ))
        self._write_readme(NAMES)
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cited line count", result.stdout)

        self._write_appendices(code_map_extra=(
            row + f"| `engine.py` | 120 | [01]({NAMES[0]}) |\n"
        ))
        result = self._run()
        self.assertNotIn("cited line count", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pointer_misroute_flagged(self) -> None:
        self._write_numbered(NAMES)
        row = "| Path | Lines | Files |\n| --- | --- | --- |\n"
        self._write_appendices(code_map_extra=(
            row + f"| `quorum/` | — | [02]({NAMES[1]}) |\n"
        ))
        self._write_readme(NAMES)
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("quorum", result.stdout)
        self.assertIn("no linked file mentions it", result.stdout)

        (self.guide / NAMES[1]).write_text(
            f"# Beta store\n\nThe quorum layer arbitrates writes.\n\n{FILLER}\n",
            encoding="utf-8",
        )
        result = self._run()
        self.assertNotIn("no linked file mentions it", result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
