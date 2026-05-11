#!/usr/bin/env python3
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.claude_review import PullRequestData, PullRequestRef, build_review, changed_paths, parse_pr_url


SAMPLE_DIFF = """diff --git a/app/auth/session.ts b/app/auth/session.ts
index 1111111..2222222 100644
--- a/app/auth/session.ts
+++ b/app/auth/session.ts
@@ -1,2 +1,3 @@
+export function requireSession() { return true; }
diff --git a/tests/session.test.ts b/tests/session.test.ts
index 3333333..4444444 100644
--- a/tests/session.test.ts
+++ b/tests/session.test.ts
@@ -1,2 +1,3 @@
+expect(requireSession()).toBe(true);
"""


class ClaudeReviewTests(unittest.TestCase):
    def test_parse_pr_url(self):
        ref = parse_pr_url("https://github.com/example/project/pull/42")
        self.assertEqual(ref.owner, "example")
        self.assertEqual(ref.repo, "project")
        self.assertEqual(ref.number, 42)

    def test_changed_paths(self):
        self.assertEqual(changed_paths(SAMPLE_DIFF), ["app/auth/session.ts", "tests/session.test.ts"])

    def test_review_has_required_sections(self):
        pr = PullRequestData(
            ref=PullRequestRef("example", "project", 42),
            title="Add session guard",
            author="reviewer",
            additions=2,
            deletions=0,
            changed_files=2,
            diff=SAMPLE_DIFF,
            url="https://github.com/example/project/pull/42",
        )
        review = build_review(pr)
        self.assertIn("### Summary of Changes", review)
        self.assertIn("### Identified Risks", review)
        self.assertIn("### Improvement Suggestions", review)
        self.assertIn("### Confidence Score: High", review)
        self.assertIn("Authentication or authorization surface", review)


if __name__ == "__main__":
    unittest.main()
