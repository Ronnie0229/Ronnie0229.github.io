#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import read_aloud_previous_release_gate as gate


class PreviousReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.sha = "a" * 40
        self.deployment = {"commit": self.sha}
        self.article = {
            "kind": "ARTICLE", "commit": self.sha,
            "rss_verified": True, "sitemap_verified": True,
            "notification_terminal": "PASS",
        }
        self.audio = {
            "kind": "AUDIO_ONLY_UPDATE", "commit": self.sha,
            "notification_policy": "NO_EMAIL", "notification_sent_count": 0,
        }

    def check(self, receipt, *, deployment=None, media_ready=False):
        return gate.validate_previous_release(
            receipt, self.deployment if deployment is None else deployment,
            page_status=200, page_contains_identity=True, media_ready=media_ready)

    def test_article_release_pass(self):
        self.assertEqual(self.check(self.article)["status"], "PREVIOUS_RELEASE_PASS")

    def test_audio_release_pass_without_email_workflow(self):
        self.assertEqual(self.check(self.audio, media_ready=True)["status"], "PREVIOUS_RELEASE_PASS")

    def test_audio_release_must_have_zero_email(self):
        for count in [1, None, "0", True]:
            with self.subTest(count=count), self.assertRaises(gate.PreflightError):
                self.check({**self.audio, "notification_sent_count": count}, media_ready=True)

    def test_audio_release_requires_media_readback(self):
        with self.assertRaises(gate.PreflightError):
            self.check(self.audio, media_ready=False)

    def test_must_verify_exact_commit(self):
        with self.assertRaises(gate.PreflightError):
            self.check(self.article, deployment={"commit": "b" * 40})

    def test_article_mail_and_feed_checks_are_mandatory(self):
        for key in ["rss_verified", "sitemap_verified", "notification_terminal"]:
            bad = dict(self.article)
            bad.pop(key)
            with self.subTest(key=key), self.assertRaises(gate.PreflightError):
                self.check(bad)

    def test_invalid_identity_rejected(self):
        with self.assertRaises(gate.PreflightError):
            self.check({**self.article, "commit": "invalid"})
        with self.assertRaises(gate.PreflightError):
            self.check({**self.article, "kind": "UNKNOWN"})

    def test_http_200_alone_is_never_enough(self):
        with self.assertRaises(gate.PreflightError):
            gate.validate_previous_release(self.article, self.deployment,
                                           page_status=200, page_contains_identity=False)


if __name__ == "__main__":
    unittest.main()
