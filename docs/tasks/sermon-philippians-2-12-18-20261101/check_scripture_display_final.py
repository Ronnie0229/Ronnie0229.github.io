from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[3]
slug="2026-11-01-腓立比书-2-12-18｜从抱怨到发光.md"
posts=ROOT/"src/content/posts"/slug
mirror=ROOT/"data/processed/整理后的讲道文章"/slug
assert posts.read_bytes()==mirror.read_bytes(),"mirror identity mismatch"
txt=posts.read_text()
body=txt.split("---",2)[-1]
labels=["腓立比书2章12节到18节：","腓立比书2章12节：","腓立比书2章14节：","腓立比书2章15节：","腓立比书2章16节：","腓立比书2章17节到18节：","腓立比书2章12节下半节到13节：","希伯来书3章16节到19节：","诗篇2章11节：","以赛亚书53章3节：","以赛亚书53章5节说：","以赛亚书53章7节：","腓立比书2章9节到11节："]
for label in labels: assert body.count(label)==1,(label,body.count(label))
assert not re.search(r"(?m)^\s*\d{1,2}b?\s+(?=[\u4e00-\u9fff])",body)
assert not re.search(r"(?<!\d)\b\d{1,2}b?\s+(?=[\u4e00-\u9fff])",body)
assert not re.search(r"(?:腓立比书|希伯来书|以赛亚书|诗篇)\s*\d+[:：]\d+",body)
assert "腓立比书2章12节到18节： 这样看来" in body
assert re.search(r"腓立比书2章9节到11节：\s*所以神将他升为至高",body)
assert "腓立比书2章12节下半节到13节： 就当恐惧战兢" in body
print(json.dumps({"pass":True,"sha256":hashlib.sha256(posts.read_bytes()).hexdigest(),"validated_labels":len(labels),"forbidden_verse_number_residue":0,"mirror_sha_match":True},ensure_ascii=False))
