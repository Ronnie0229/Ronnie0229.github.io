import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import read_aloud_new_post_executor as executor
import read_aloud_new_post_delivery as delivery
import read_aloud_audio_site_publisher as publisher


class PilotEntrypointDenyTests(unittest.TestCase):
    def test_missing_pilot_grant_rejected_at_every_side_effect_entry(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            missing = root / "not-authorized.json"
            with self.assertRaises(executor.IntakeExecutionError):
                executor.execute_one(root, root, pilot_grant_path=missing)
            with self.assertRaises(delivery.ReadyDeliveryError):
                delivery.deliver_one(root, root, pilot_grant_path=missing)
            with self.assertRaises(publisher.AudioPublicationError):
                publisher.publish_one(root, root, pilot_grant_path=missing, allow_test_repo=True, build=False)

    def test_wrong_grant_rejected_before_effects(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bad = root / "bad.json"
            bad.write_text('{"schema":"invalid"}')
            with patch.object(executor.wf, "start_workflow") as start, \
                 patch.object(delivery, "archive_wav") as nas, \
                 patch.object(delivery, "upload_r2") as r2, \
                 patch.object(publisher, "run_git") as git:
                with self.assertRaises(executor.IntakeExecutionError):
                    executor.execute_one(root, root, pilot_grant_path=bad)
                with self.assertRaises(delivery.ReadyDeliveryError):
                    delivery.deliver_one(root, root, pilot_grant_path=bad)
                with self.assertRaises(publisher.AudioPublicationError):
                    publisher.publish_one(root, root, pilot_grant_path=bad, allow_test_repo=True, build=False)
                start.assert_not_called()
                nas.assert_not_called()
                r2.assert_not_called()
                git.assert_not_called()


if __name__ == "__main__":
    unittest.main()
