#!/usr/bin/env python3
"""Offline package and CLI checks; this does not validate an article's meaning."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "yomiyasu"
FIXTURES = ROOT / "tests" / "yomiyasu"
MANIFEST = ROOT / ".agents" / "yomiyasu-upstream.json"
COMMIT = "373356eb874af5184962c88e925ea7eb58450318"


def git_blob_sha1(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class PackageTests(unittest.TestCase):
    def test_pin_and_all_upstream_bytes(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["repository"], "https://github.com/nanaism/yomiyasu")
        self.assertEqual(manifest["tag"], "v1.1.1")
        self.assertEqual(manifest["commit"], COMMIT)
        self.assertEqual(len(manifest["files"]), 17)
        for item in manifest["files"]:
            with self.subTest(path=item["path"]):
                path = (ROOT / item["path"]).resolve()
                self.assertTrue(path.is_relative_to(SKILL.resolve()))
                self.assertEqual(git_blob_sha1(path), item["git_blob_sha1"])
        self.assertIn("Copyright (c) 2026 nanaism", (SKILL / "LICENSE").read_text(encoding="utf-8"))
        self.assertIn("UNICODE LICENSE V3", (SKILL / "UNICODE-LICENSE.txt").read_text(encoding="utf-8"))

    def test_skill_relative_resources(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        resources = set(re.findall(r"(?:references|scripts)/[A-Za-z0-9_./-]+\.(?:md|py)", text))
        resources.update({
            "references/domains/tech.md", "references/domains/business.md",
            "references/domains/essay.md", "scripts/markdown_visibility.py",
            "assets/algo-artis.png",
        })
        self.assertGreaterEqual(len(resources), 9)
        for relative in resources:
            with self.subTest(path=relative):
                self.assertTrue((SKILL / relative).is_file())

    def test_runtime_imports_are_local_or_stdlib(self):
        # Audit imports before loading the vendored tests or CLI code.
        forbidden = {"urllib", "http", "socket", "subprocess", "requests"}
        for path in sorted((SKILL / "scripts").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = [node.module]
                for module in modules:
                    root = module.split(".")[0]
                    with self.subTest(script=path.name, module=module):
                        self.assertNotIn(root, forbidden)
                        self.assertTrue(root in sys.stdlib_module_names or root == "markdown_visibility")


class CliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="yomiyasu outside checkout ")
        self.addCleanup(temporary.cleanup)
        self.cwd = Path(temporary.name)

    def run_cli(self, script, *args, stdin=None):
        # Isolated mode also exercises the scripts' sibling-module fallback.
        return subprocess.run(
            [sys.executable, "-I", "-B", str(SKILL / "scripts" / script), *map(str, args)],
            input=stdin, cwd=self.cwd, capture_output=True, timeout=15,
        )

    def json_result(self, process):
        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8", "replace"))
        return json.loads(process.stdout.decode("utf-8"))

    def test_lint_file_and_utf8_stdin_from_unrelated_cwd(self):
        sample = FIXTURES / "before.md"
        original_bytes = sample.read_bytes()
        report = self.json_result(self.run_cli("yomiyasu_lint.py", sample, "--json"))
        streamed = self.json_result(self.run_cli("yomiyasu_lint.py", "--json", stdin=original_bytes))
        self.assertEqual(report, streamed)
        self.assertTrue(any(item["rule"] == "meta_intro" for item in report["findings"]))
        front_end = sample.read_text(encoding="utf-8").splitlines().index("---", 1) + 1
        self.assertTrue(all(item["line"] > front_end for item in report["findings"]))
        self.assertEqual(sample.read_bytes(), original_bytes)

    def test_diff_file_and_stance_from_unrelated_cwd(self):
        before, after = FIXTURES / "before.md", FIXTURES / "after.md"
        saved = [path.read_bytes() for path in (before, after)]
        report = self.json_result(self.run_cli(
            "yomiyasu_diff.py", before, after, "--stance=説明", "--json",
        ))
        self.assertEqual(report["endings"]["stance"], "説明")
        self.assertTrue(report["lost_words"])
        self.assertEqual([path.read_bytes() for path in (before, after)], saved)

    def test_cli_errors_are_not_silently_successful(self):
        self.assertEqual(self.run_cli("yomiyasu_lint.py", self.cwd / "missing.md").returncode, 2)
        self.assertEqual(self.run_cli("yomiyasu_diff.py").returncode, 1)

    def test_numeric_changes_still_need_raw_diff_review(self):
        before, after = self.cwd / "before.md", self.cwd / "after.md"
        before.write_text("タイムアウトは30秒です。\n", encoding="utf-8")
        after.write_text("タイムアウトは3秒です。\n", encoding="utf-8")
        report = self.json_result(self.run_cli("yomiyasu_diff.py", before, after, "--json"))
        # v1.1.1's word extraction omits standalone numbers.
        self.assertEqual(report["new_words"], [])
        self.assertEqual(report["lost_words"], [])
        self.assertEqual(report["markers"], [])
        self.assertNotEqual(before.read_text(encoding="utf-8"), after.read_text(encoding="utf-8"))

    def test_sample_rewrite_preserves_technical_and_claim_content(self):
        before = (FIXTURES / "before.md").read_text(encoding="utf-8")
        after = (FIXTURES / "after.md").read_text(encoding="utf-8")
        # This fixture edits only a redundant introduction; it is not a general semantic check.
        self.assertEqual(after, before.replace("本記事では、", "", 1))
        protected = r"(?ms)\A---\n.*?\n---|^\x60\x60\x60[^\n]*\n.*?^\x60\x60\x60$|\x60[^\x60\n]+\x60"
        self.assertEqual(re.findall(protected, before), re.findall(protected, after))


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or newer is required.")
    # Keep tests read-only outside their temporary directories.
    sys.dont_write_bytecode = True
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PackageTests)
    audit = unittest.TextTestRunner(verbosity=2).run(suite)
    if not audit.wasSuccessful():
        return 1
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CliTests)
    suite.addTests(unittest.defaultTestLoader.discover(str(SKILL / "tests"), pattern="test_*.py"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("Verified yomiyasu v1.1.1: pinned bytes, resources, offline CLI, and upstream regressions.")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
