#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from read_aloud_publication_lock import (
    SCHEMA, last_receipt, mark_previous_verified_under_lock,
    publication_lock, record_pending_under_lock,
)
from read_aloud_previous_release_gate import PreflightError


class PublicationLockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.receipt = {
            "schema": SCHEMA, "kind": "AUDIO_ONLY_UPDATE",
            "commit": "c" * 40,
            "publication_state": "PUBLISHED_PENDING_NEXT_PREFLIGHT_VERIFY",
            "notification_policy": "NO_EMAIL",
            "notification_sent_count": 0,
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_pending_blocks_overlapping_release_until_verified(self):
        with publication_lock(self.root):
            record_pending_under_lock(self.root, self.receipt)
            with self.assertRaises(PreflightError):
                record_pending_under_lock(self.root, dict(self.receipt, commit="d" * 40))
            self.assertEqual(last_receipt(self.root)["commit"], "c" * 40)
            mark_previous_verified_under_lock(self.root, "c" * 40)
            self.assertEqual(last_receipt(self.root)["publication_state"], "VERIFIED")
            record_pending_under_lock(self.root, dict(self.receipt, commit="d" * 40))
            self.assertEqual(last_receipt(self.root)["commit"], "d" * 40)

    def test_audio_email_nonzero_blocks(self):
        with publication_lock(self.root):
            for value in (1, True, None, "0"):
                with self.subTest(value=value), self.assertRaises(PreflightError):
                    record_pending_under_lock(self.root, dict(self.receipt, notification_sent_count=value))

    def test_wrong_verification_commit_fails(self):
        with publication_lock(self.root):
            record_pending_under_lock(self.root, self.receipt)
            with self.assertRaises(PreflightError):
                mark_previous_verified_under_lock(self.root, "d" * 40)


if __name__ == "__main__":
    unittest.main()
