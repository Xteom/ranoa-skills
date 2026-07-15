#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_guide.py")


class ValidateGuideTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.guide = self.repo / "guide"
        self.guide.mkdir(parents=True)
        self.source = self.repo / "src.py"
        self.source.write_text("def run():\n    return 1\n\nresult = run()\n", encoding="utf-8")
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

    def test_valid_guide_passes(self) -> None:
        for name in ("01-a.md", "02-b.md", "03-c.md", "04-d.md"):
            (self.guide / name).write_text(f"# {name}\n", encoding="utf-8")
        self.guide.joinpath("README.md").write_text(
            "# Guide\n" + self._metadata()
            + "\n".join(f"[{name}]({name})" for name in ("01-a.md", "02-b.md", "03-c.md", "04-d.md"))
            + "\n\nSource: [implementation](../src.py#L1-L4)\n"
            + "```python\ndef run():\n    return 1\n```\n"
            + "```python\nresult = run()\n```\n"
            + "```mermaid\nflowchart LR\nA --> B\n```\n"
            + "```mermaid\nsequenceDiagram\nA->>B: call\n```\n",
            encoding="utf-8",
        )
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fake_evidence_and_plain_filenames_do_not_pass(self) -> None:
        for name in ("01-a.md", "02-b.md", "03-c.md", "04-d.md"):
            (self.guide / name).write_text(f"# {name}\n", encoding="utf-8")
        self.guide.joinpath("README.md").write_text(
            "# Guide\n" + self._metadata()
            + "01-a.md 02-b.md 03-c.md 04-d.md\n"
            + "\nSource: [implementation](../src.py)\n"
            + "```python\nnot_in_source()\n```\n```python\nalso_fake()\n```\n"
            + "```mermaid\nx\n```\n```mermaid\ny\n```\n",
            encoding="utf-8",
        )
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not link", result.stdout)
        self.assertIn("non-empty Mermaid", result.stdout)
        self.assertIn("source snippets", result.stdout)


if __name__ == "__main__":
    unittest.main()
