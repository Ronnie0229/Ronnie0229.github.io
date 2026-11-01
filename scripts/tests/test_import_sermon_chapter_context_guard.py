import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from import_sermons import resolve_scripture,same_chapter_context_does_not_conflict
class ChapterMentionGuard(unittest.TestCase):
 def test_same_chapter_only_does_not_override_exact_range(self):
  folder="腓立比书2章12节到18节_从抱怨到发光"
  file=Path("20261101_腓立比书2章12节到18节_从抱怨到发光_Patrick_中文.txt")
  self.assertEqual(resolve_scripture(folder,file,"大家好，我们继续查考腓立比书第二章"),("腓立比书 2:12-18","high"))
 def test_different_chapter_rejected(self):
  self.assertFalse(same_chapter_context_does_not_conflict("腓立比书 2:12-18","腓立比书 3"))
 def test_different_book_rejected(self):
  self.assertFalse(same_chapter_context_does_not_conflict("腓立比书 2:12-18","以弗所书 2"))
 def test_specific_outside_range_rejected(self):
  self.assertFalse(same_chapter_context_does_not_conflict("腓立比书 2:12-18","腓立比书 2:19"))
if __name__=="__main__":unittest.main()
