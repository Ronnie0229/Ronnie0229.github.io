from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3]
NAME="2026-11-01-腓立比书-2-12-18｜从抱怨到发光.md"
paths=[ROOT/"src/content/posts"/NAME,ROOT/"data/processed/整理后的讲道文章"/NAME]
original=[p.read_text() for p in paths]
assert original[0]==original[1],"mirror not equal before edit"
text=original[0]
# Exact consecutive scripture runs, not prose paragraphs or speaker narrative.
groups=[tuple(str(x) for x in range(12,19)),("17","18","19"),("12b","13"),("9","10","11")]
report=[]
for group in groups:
    # require every verse as a single full paragraph, with exact ordered, adjacent positions
    pieces=text.split("\n\n")
    candidates=[]
    for i in range(len(pieces)-len(group)+1):
        if all(re.match(r"^"+re.escape(n)+r"\s+\S",pieces[i+j]) for j,n in enumerate(group)):
            candidates.append(i)
    if len(candidates)!=1:raise RuntimeError(f"expected one exact run {group}, found {candidates}")
    i=candidates[0]
    before="\n\n".join(pieces[i:i+len(group)])
    after="\n".join(pieces[i:i+len(group)])
    assert before in text
    text=text.replace(before,after,1)
    report.append({"verses":group,"before":hashlib.sha256(before.encode()).hexdigest(),"after":hashlib.sha256(after.encode()).hexdigest()})
assert text!=original[0]
# SHA identity: removal of 2 newlines per join only; all content preserved.
assert re.sub(r"\s+","",text)==re.sub(r"\s+","",original[0])
for p in paths:p.write_text(text)
print(json.dumps({"status":"TEXT_EXACT_DISPLAY_REPAIR","groups":report,"site_post_sha":hashlib.sha256(text.encode()).hexdigest(),"mirror_exact":paths[1].read_text()==paths[0].read_text()},ensure_ascii=False,indent=2))
