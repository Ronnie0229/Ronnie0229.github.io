import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from read_aloud_exact_one_pilot_grant import (
    ALLOWED, SCHEMA, PATRICK_ID, PATRICK_POST, PilotGrantError, validate_exact_one
)


class ExactOneGrantTests(unittest.TestCase):
    def setUp(self):
        self.body = ('---\narticleId: "' + PATRICK_ID + '"\ntitle: "活着就是基督"\n---\n完整正文\n').encode()
        self.grant = dict(
            schema=SCHEMA, article_id=PATRICK_ID, post_path=PATRICK_POST,
            source_sha256=hashlib.sha256(self.body).hexdigest(),
            operation_classes=list(ALLOWED), authorization_ref="owner-exact-one",
            future_posts_enabled=False, historical_backfill=False
        )

    def test_only_exact_one_pilot_is_eligible(self):
        result = validate_exact_one(self.grant, self.body)
        self.assertEqual(result["article_id"], PATRICK_ID)
        self.assertFalse(result["ongoing_automation_enabled"])

    def test_future_post_selector_permission_is_rejected(self):
        for field in ("allow_unattended_tts", "allow_unattended_publication", "last_processed_commit"):
            with self.subTest(field=field), self.assertRaises(PilotGrantError):
                validate_exact_one(dict(self.grant, **{field: True}), self.body)
        with self.assertRaises(PilotGrantError):
            validate_exact_one(dict(self.grant, future_posts_enabled=True), self.body)

    def test_other_article_and_sha_drift_rejected(self):
        with self.assertRaises(PilotGrantError):
            validate_exact_one(dict(self.grant, article_id="post-wrong"), self.body)
        with self.assertRaises(PilotGrantError):
            validate_exact_one(self.grant, self.body + b"changed")
        with self.assertRaises(PilotGrantError):
            validate_exact_one(self.grant, self.body, article_id="post-other")

    def test_stage_claim_is_durable_and_replay_denied(self):
        from read_aloud_exact_one_pilot_grant import claim_pilot_stage
        verified = {"article_id": PATRICK_ID, "source_sha256": self.grant["source_sha256"],
                    "authorization_ref": self.grant["authorization_ref"]}
        with tempfile.TemporaryDirectory() as d:
            claimed = claim_pilot_stage(Path(d), "TTS_ONCE", verified)
            self.assertTrue(claimed.is_file())
            with self.assertRaisesRegex(PilotGrantError, "PILOT_STAGE_ALREADY_CLAIMED_NO_REPLAY"):
                claim_pilot_stage(Path(d), "TTS_ONCE", verified)
            self.assertTrue(claim_pilot_stage(Path(d), "NAS_WAV_APPEND_ONLY", verified).is_file())

    def test_existing_audio_rejected(self):
        changed = self.body.replace(b'\n---\n', b'\naudioUrl: "https://example.com/audio.mp3"\n---\n')
        with self.assertRaises(PilotGrantError):
            validate_exact_one(dict(self.grant, source_sha256=hashlib.sha256(changed).hexdigest()), changed)


if __name__ == "__main__":
    unittest.main()
