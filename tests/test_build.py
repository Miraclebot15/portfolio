#!/usr/bin/env python3
"""Unit tests for the generator. Each test builds a throwaway copy of the repo.

Run:  python3 -m unittest discover -s tests -v
"""
import json, os, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = shutil.ignore_patterns(".git", "node_modules", "__pycache__")


def read(path, binary=False):
    with open(path, "rb" if binary else "r", **({} if binary else {"encoding": "utf-8"})) as f:
        return f.read()


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="portfolio-test-")
        self.repo = os.path.join(self.tmp, "repo")
        shutil.copytree(ROOT, self.repo, ignore=SKIP)
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_build(self, *args):
        return subprocess.run([sys.executable, "build.py", *args], cwd=self.repo, capture_output=True, text=True)

    def edit_json(self, rel, fn):
        path = os.path.join(self.repo, rel)
        data = json.loads(read(path))
        fn(data)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)

    def assert_fails(self, result, text):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(text, result.stdout + result.stderr)

    # ---- the clean repo -------------------------------------------------
    def test_clean_repo_passes_check(self):
        r = self.run_build("--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_build_is_deterministic(self):
        self.assertEqual(self.run_build().returncode, 0)
        first = {f: read(os.path.join(self.repo, f), True) for f in os.listdir(self.repo) if f.endswith((".html", ".xml", ".txt", ".svg"))}
        self.assertEqual(self.run_build().returncode, 0)
        for f, b in first.items():
            self.assertEqual(b, read(os.path.join(self.repo, f), True), f)

    def test_sitemap_excludes_404(self):
        sm = read(os.path.join(self.repo, "sitemap.xml"))
        self.assertNotIn("404.html", sm)
        self.assertIn("nexus-core.html", sm)

    # ---- --check ----------------------------------------------------------
    def test_check_flags_stale_file(self):
        with open(os.path.join(self.repo, "about.html"), "a", encoding="utf-8") as f: f.write("\n<!-- edited by hand -->")
        r = self.run_build("--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("stale or missing: about.html", r.stdout)

    def test_check_flags_missing_file(self):
        os.remove(os.path.join(self.repo, "contact.html"))
        r = self.run_build("--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("contact.html", r.stdout)

    def test_check_flags_orphan(self):
        with open(os.path.join(self.repo, "old-page.html"), "w") as f: f.write("<html></html>")
        r = self.run_build("--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("orphan", r.stdout)
        self.assertIn("old-page.html", r.stdout)

    # ---- content validation ----------------------------------------------
    def test_rejects_bad_slug(self):
        self.edit_json("content/projects.json", lambda d: d[0].update(slug="Bad Slug"))
        self.assert_fails(self.run_build(), "slug must be lowercase")

    def test_rejects_duplicate_slug(self):
        self.edit_json("content/projects.json", lambda d: d[1].update(slug=d[0]["slug"]))
        self.assert_fails(self.run_build(), "duplicated or reserved")

    def test_rejects_reserved_slug(self):
        self.edit_json("content/projects.json", lambda d: d[0].update(slug="contact"))
        self.assert_fails(self.run_build(), "duplicated or reserved")

    def test_rejects_unknown_state(self):
        self.edit_json("content/projects.json", lambda d: d[0].update(state="Maybe"))
        self.assert_fails(self.run_build(), "state 'Maybe'")

    def test_rejects_unknown_motif_and_bad_color(self):
        def f(d): d[0].update(motif="nope", color="red")
        self.edit_json("content/projects.json", f)
        r = self.run_build()
        self.assert_fails(r, "unknown motif 'nope'")
        self.assertIn("color must look like", r.stdout + r.stderr)

    def test_rejects_non_https_url(self):
        self.edit_json("content/projects.json", lambda d: d[0].update(url="http://example.com"))
        self.assert_fails(self.run_build(), "url must start with https://")

    def test_rejects_missing_status_function(self):
        self.edit_json("content/projects.json", lambda d: d[0].update(check="/api/does-not-exist"))
        self.assert_fails(self.run_build(), "has no matching file in api/")

    def test_rejects_unknown_stack_icon(self):
        self.edit_json("content/site.json", lambda d: d["stack"][1]["items"][0].update(i="no-such-icon"))
        self.assert_fails(self.run_build(), "unknown icon id 'no-such-icon'")

    def test_rejects_ai_provider_in_stack(self):
        self.edit_json("content/site.json", lambda d: d["stack"][1]["items"].append({"name": "OpenAI"}))
        self.assert_fails(self.run_build(), "AI model or provider name")

    def test_rejects_ai_provider_in_project_tech(self):
        self.edit_json("content/projects.json", lambda d: d[0].update(tech=["Python", "Gemini"]))
        self.assert_fails(self.run_build(), "AI model or provider name in tech")

    def test_rejects_note_with_missing_project(self):
        self.edit_json("content/notes.json", lambda d: d[0].update(project="ghost"))
        self.assert_fails(self.run_build(), "project 'ghost' does not exist")

    def test_rejects_bad_note_kind_and_empty_section(self):
        def f(d): d[0].update(kind="Opinion"); d[0]["sections"][0]["p"] = []
        self.edit_json("content/notes.json", f)
        r = self.run_build()
        self.assert_fails(r, "kind must be one of")
        self.assertIn("section 1 needs", r.stdout + r.stderr)

    # ---- output validation ------------------------------------------------
    def test_rejects_dash_in_output(self):
        self.edit_json("content/projects.json", lambda d: d[0].update(purpose="A thing \u2014 with a dash"))
        self.assert_fails(self.run_build(), "em or en dash found")

    def test_rejects_broken_internal_link(self):
        path = os.path.join(self.repo, "content/landing.html")
        with open(path, "a", encoding="utf-8") as f: f.write('\n<a href="missing-page.html">x</a>')
        self.assert_fails(self.run_build(), "broken link or asset 'missing-page.html'")

    def test_rejects_broken_anchor(self):
        path = os.path.join(self.repo, "content/landing.html")
        with open(path, "a", encoding="utf-8") as f: f.write('\n<a href="about.html#nope-anchor">x</a>')
        self.assert_fails(self.run_build(), "anchor 'about.html#nope-anchor' not found")

    def test_failed_build_writes_nothing(self):
        before = read(os.path.join(self.repo, "index.html"), True)
        self.edit_json("content/projects.json", lambda d: d[0].update(state="Maybe"))
        self.assertNotEqual(self.run_build().returncode, 0)
        self.assertEqual(before, read(os.path.join(self.repo, "index.html"), True))


if __name__ == "__main__":
    unittest.main()
