from pathlib import Path
import re,json,hashlib
root=Path(__file__).resolve().parents[3]
n="2026-11-01-腓立比书-2-12-18｜从抱怨到发光.md"
paths=[root/"src/content/posts"/n,root/"data/processed/整理后的讲道文章"/n]
s=paths[0].read_text();assert s==paths[1].read_text()
replacements={
"请看第十四节。14 凡所行的":"请看第十四节。\n\n腓立比书2章14节： 凡所行的",
"以赛亚书 53:5 说：5 哪知":"以赛亚书53章5节说：哪知",
"2. 重读腓立比书 2:12–16。":"2. 重读腓立比书2章12节到16节。",
}
for old,new in replacements.items():
 assert s.count(old)==1,(old,s.count(old))
 s=s.replace(old,new)
for p in paths:p.write_text(s)
print(json.dumps({"sha256":hashlib.sha256(s.encode()).hexdigest(),"mirror":paths[0].read_bytes()==paths[1].read_bytes()},ensure_ascii=False))
