from pathlib import Path
import re,hashlib,json
root=Path(__file__).resolve().parents[3]
name="2026-11-01-腓立比书-2-12-18｜从抱怨到发光.md"
paths=[root/"src/content/posts"/name,root/"data/processed/整理后的讲道文章"/name]
a=paths[0].read_text();assert a==paths[1].read_text()
before=hashlib.sha256(a.encode()).hexdigest()
# Display-only replacements bound to exactly known verse fragments, preserving all controlled verse characters.
rules=[
(r'(?m)^12 (?=这样看来)',"腓立比书2章12节到18节： "),
(r'(?m)^13 (?=因为你们立志行事)',""),
(r'(?m)^14 (?=凡所行的)',""),
(r'(?m)^15 (?=使你们无可指摘)',""),
(r'(?m)^16 (?=将生命的道表明出来)',""),
(r'(?m)^17 (?=我以你们的信心为供献的祭物)',""),
(r'(?m)^18 (?=你们也要照样喜乐)',""),
(r'(?m)^12 (?=这样看来)',""),
]
# Main excerpt independently; avoid first verse regex touching later narrative by scoped block.
start=a.index("\n12 这样看来");end=a.index("\n\n我上大学时",start)
frag=a[start:end];frag=re.sub(r'^\n12 ', "\n腓立比书2章12节到18节： ",frag)
frag=re.sub(r'(?m)^(?:13|14|15|16|17|18) ', "",frag)
frag=frag.replace("\n","")
a=a[:start]+frag+a[end:]
# Other direct quotations only: anchored concrete sequences or source-introduction boundaries.
repls=[
("12 这样看来，我亲爱的弟兄","腓立比书2章12节： 这样看来，我亲爱的弟兄"),
("15 使你们无可指摘","腓立比书2章15节： 使你们无可指摘"),
("16 将生命的道表明出来","腓立比书2章16节： 将生命的道表明出来"),
("请看保罗在第十七至十八节的态度：17 ","请看保罗在第十七至十八节的态度：腓立比书2章17节到18节： "),
("圣经在希伯来书第三章这样说：16 ","圣经在希伯来书第三章这样说——希伯来书3章16节到19节： "),
("12b 就当恐惧战兢","腓立比书2章12节下半节到13节： 就当恐惧战兢"),
("请看诗篇 2:11：11 ","请看诗篇2章11节： "),
("以赛亚书第五十三章却这样论到祂：3 ","以赛亚书第五十三章却这样论到祂——以赛亚书53章3节： "),
("以赛亚书第五十三章继续说：7 ","以赛亚书第五十三章继续说——以赛亚书53章7节： "),
]
for old,new in repls:
 assert a.count(old)==1,(old,a.count(old))
 a=a.replace(old,new)
# Number on the second verse of 17-18 quote, and 12b-13 slides.
a=a.replace("\n\n18 你们也要照样喜乐","\n\n你们也要照样喜乐")
a=a.replace("\n13 因为你们立志行事","\n因为你们立志行事")
# Hebrews consecutive passage, with no per-verse numerals or paragraph breaks inside citation.
for v in ("17","18","19"):
 old="\n"+v+" "
 assert old in a
 a=a.replace(old,"",1)
# doxology: preserve heading then one full passage label with no verse numerals
old="**颂赞——腓立比书 2:9–11**"
assert a.count(old)==1
a=a.replace(old,"**颂赞——腓立比书2章9节到11节**\n\n腓立比书2章9节到11节：")
for v in ("9","10","11"):
 assert a.count("\n"+v+" ")==1,(v,a.count("\n"+v+" "))
 a=a.replace("\n"+v+" ","",1)
# Never change verse characters: only labels/delimiters and explicit numeral removal.
assert "12b " not in a
assert not re.search(r'(?m)^\d{1,2}\s',a)
for p in paths:p.write_text(a)
print(json.dumps({"status":"DISPLAY_REMEDIATED","before_sha":before,"after_sha":hashlib.sha256(a.encode()).hexdigest(),"mirror_equal":paths[0].read_bytes()==paths[1].read_bytes()},ensure_ascii=False))
