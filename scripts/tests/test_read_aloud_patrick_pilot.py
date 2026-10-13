import sys
import json
import hashlib
import threading
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import read_aloud_patrick_pilot as pilot
from read_aloud_exact_one_pilot_grant import PilotGrantError

class PatrickPilotRunnerTests(unittest.TestCase):
    def test_invalid_grant_cannot_trigger_any_stage(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            grant=root/'absent.json'
            with patch.object(pilot, "execute_one") as tts, patch.object(pilot, "deliver_one") as media, patch.object(pilot, "publish_one") as website:
                for s in ("register","tts","media","publish"):
                    with self.subTest(stage=s), self.assertRaises(PilotGrantError):
                        pilot.stage(root,root,grant,s)
                tts.assert_not_called()
                media.assert_not_called()
                website.assert_not_called()

    def test_atomic_register_two_contenders_one_winner(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            frozen = {"article_id": pilot.PATRICK_ID, "source_commit": "a"*40,
                      "post_sha256": "b"*64, "authorization_ref": "owner-exact-one",
                      "post_path": pilot.PATRICK_POST}
            results = []
            with patch.object(pilot, "preflight", return_value=frozen):
                def worker():
                    try:
                        results.append(("pass", pilot.stage(root, root, root/"grant.json", "register")))
                    except pilot.PilotDriverError as exc:
                        results.append(("blocked", str(exc)))
                threads = [threading.Thread(target=worker) for _ in range(2)]
                for thread in threads: thread.start()
                for thread in threads: thread.join()
            self.assertEqual(sum(x[0]=="pass" for x in results), 1, results)
            self.assertEqual(sum(x[0]=="blocked" for x in results), 1, results)
            self.assertEqual(len(list((root/"new-post-intake").glob("*.json"))), 1)

    def test_s4_stage_uses_direct_bounded_workflow_not_future_selector(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            frozen = {"article_id": pilot.PATRICK_ID, "source_commit": "a"*40,
                      "post_sha256": "b"*64, "authorization_ref": "owner-exact-one",
                      "post_path": pilot.PATRICK_POST}
            identity = hashlib.sha256((frozen["source_commit"]+"\n"+pilot.PATRICK_ID).encode()).hexdigest()
            intake = root/"new-post-intake"/f"{identity}.json"
            intake.parent.mkdir()
            intake.write_text(json.dumps({"authorization_ref":"owner-exact-one",
                "post": {"post_sha256":"b"*64}, "status":"S4_WORKFLOW_REGISTERED",
                "workflow_id":"c"*64}))
            workflow = {"state":"RENDER_READY","descriptor":{
                "authorization_ref":"owner-exact-one","article_id":pilot.PATRICK_ID}}
            with patch.object(pilot,"preflight",return_value=frozen), \
                 patch("read_aloud_workflow.workflow_status",return_value=workflow), \
                 patch("read_aloud_workflow.tick_workflow",return_value={
                    "state":"TTS_SUBMITTED"}) as tick:
                result=pilot.stage(root,root,root/"grant.json","s4")
            self.assertEqual(result["state"],"TTS_SUBMITTED")
            tick.assert_called_once_with(root,"c"*64)

    def test_all_pilot_stages_connect_with_mocked_side_effects(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            frozen = {"article_id": pilot.PATRICK_ID, "source_commit":"a"*40,
                      "post_sha256":"b"*64,"authorization_ref":"owner-exact-one",
                      "post_path":pilot.PATRICK_POST}
            identity = hashlib.sha256((frozen["source_commit"]+"\n"+pilot.PATRICK_ID).encode()).hexdigest()
            with patch.object(pilot, "preflight", return_value=frozen):
                self.assertEqual(pilot.stage(root,root,root/"grant.json","register")["status"],"PILOT_REGISTERED")
                with patch.object(pilot, "execute_one", return_value={"post":{"article_id":pilot.PATRICK_ID}}) as tts:
                    self.assertEqual(pilot.stage(root,root,root/"grant.json","tts")["status"],"PILOT_STAGE_INVOKED")
                    self.assertEqual(tts.call_args.kwargs["pilot_grant_path"],root/"grant.json")
                intake = root/"new-post-intake"/f"{identity}.json"
                record = json.loads(intake.read_text())
                record.update(status="S4_WORKFLOW_REGISTERED",workflow_id="c"*64)
                intake.write_text(json.dumps(record))
                with patch("read_aloud_workflow.workflow_status",return_value={"state":"RENDER_READY", "descriptor":{"article_id":pilot.PATRICK_ID,"authorization_ref":"owner-exact-one"}}), patch("read_aloud_workflow.tick_workflow",return_value={"state":"AUDIO_READY_PENDING_PUBLICATION_GATE"}) as tick:
                    self.assertEqual(pilot.stage(root,root,root/"grant.json","s4")["state"],"AUDIO_READY_PENDING_PUBLICATION_GATE")
                    tick.assert_called_once()
                with patch.object(pilot,"deliver_one",return_value={"post":{"article_id":pilot.PATRICK_ID}}) as media:
                    self.assertEqual(pilot.stage(root,root,root/"grant.json","media")["status"],"PILOT_STAGE_INVOKED")
                    self.assertEqual(media.call_args.kwargs["pilot_grant_path"],root/"grant.json")
                with patch.object(pilot,"publish_one",return_value={"post":{"article_id":pilot.PATRICK_ID}}) as publish:
                    self.assertEqual(pilot.stage(root,root,root/"grant.json","publish")["status"],"PILOT_STAGE_INVOKED")
                    self.assertEqual(publish.call_args.kwargs["pilot_grant_path"],root/"grant.json")
                with self.assertRaisesRegex(pilot.PilotDriverError,"ALREADY_EXISTS"):
                    pilot.stage(root,root,root/"grant.json","register")

    def test_no_selector_or_dirty_git_is_admission_block(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            identity={"authorization_ref":"exact-one","source_sha256":"a"*64}
            with patch.object(pilot,"require_pilot_stage",return_value=identity), patch.object(pilot,"_git",return_value=""):
                (root/"new-post-automation-selector.json").write_text("{}")
                with self.assertRaisesRegex(pilot.PilotDriverError, "SELECTOR_MUST_BE_ABSENT"):
                    pilot.preflight(root,root,root/"grant.json")
                (root/"new-post-automation-selector.json").unlink()
                with patch.object(pilot,"_git",return_value="dirty"):
                    with self.assertRaisesRegex(pilot.PilotDriverError,"CANONICAL_GIT_DIRTY"):
                        pilot.preflight(root,root,root/"grant.json")

if __name__=="__main__":
    unittest.main()
