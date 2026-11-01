from pathlib import Path
import re,hashlib,json
root=Path(__file__).resolve().parents[3]
name="2026-11-01-腓立比书-2-12-18｜从抱怨到发光.md"
ps=[root/"src/content/posts"/name,root/"data/processed/整理后的讲道文章"/name]
s=ps[0].read_text();assert s==ps[1].read_text()
patches=[
("圣经在希伯来书第三章这样说——希伯来书3章16节到19节： ","圣经在希伯来书第三章这样说：\n\n希伯来书3章16节到19节： "),
("岂不是跟着摩西从埃及出来的众人吗？\n神四十年之久","岂不是跟着摩西从埃及出来的众人吗？神四十年之久"),
("请看保罗在第十七至十八节的态度：腓立比书2章17节到18节： ","请看保罗在第十七至十八节的态度：\n\n腓立比书2章17节到18节： "),
("也是喜乐，并且与你们众人一同喜乐。\n\n你们也要照样喜乐","也是喜乐，并且与你们众人一同喜乐。你们也要照样喜乐"),
("做成你们得救的工夫。\n因为你们立志行事","做成你们得救的工夫。因为你们立志行事"),
("**颂赞——腓立比书2章9节到11节**\n\n腓立比书2章9节到11节：\n","**颂赞**\n\n腓立比书2章9节到11节： "),
("请看诗篇2章11节： ","请看诗篇2章11节： "),
("以赛亚书第五十三章却这样论到祂——以赛亚书53章3节： ","以赛亚书第五十三章却这样论到祂：\n\n以赛亚书53章3节： "),
("以赛亚书第五十三章继续说——以赛亚书53章7节： ","以赛亚书第五十三章继续说：\n\n以赛亚书53章7节： "),
]
for a,b in patches:
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,b)
# Single verse quotations not allowed to have verse numbers; labels must be present.
required=["腓立比书2章12节到18节：","腓立比书2章12节：","腓立比书2章15节：","腓立比书2章16节：","腓立比书2章17节到18节：","腓立比书2章12节下半节到13节：","希伯来书3章16节到19节：","诗篇2章11节：","以赛亚书53章3节：","以赛亚书53章7节：","腓立比书2章9节到11节："]
assert all(s.count(x)==1 for x in required),[(x,s.count(x)) for x in required]
assert not re.search(r"(?m)^\d{1,2}b?\s",s)
for p in ps:p.write_text(s)
print(json.dumps({"sha256":hashlib.sha256(s.encode()).hexdigest(),"exact_mirror":ps[0].read_bytes()==ps[1].read_bytes(),"labels":len(required)},ensure_ascii=False))
