from pathlib import Path
import json,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
TITLE="腓立比书 2:5-11｜基督的道路"
EXPECTED_ARTICLE_ID="post-e6cc3489e406b568"
SENTENCE="我们来到第二章，学习圣经中一段非常著名的经文"
def get(url):
 p=subprocess.run(["curl","--fail","--silent","--show-error","--location","--max-time","18",url],capture_output=True)
 if p.returncode:raise RuntimeError("HTTPS fetch failed: "+url+" "+p.stderr.decode()[:400])
 return p.stdout.decode("utf-8",errors="replace")
rss=get("https://ronniecross.com/rss.xml")
items=ET.fromstring(rss).findall("./channel/item")
matching=[it for it in items if it.findtext("title")==TITLE]
assert len(matching)==1, "previous published item absent/duplicate from RSS"
link=matching[0].findtext("link")
page=get(link)
local_post=ROOT/"src/content/posts/2026-10-25-腓立比书-2-5-11｜基督的道路.md"
assert local_post.is_file() and EXPECTED_ARTICLE_ID in local_post.read_text()
page_checks={"title":TITLE in page,"body_sentence":SENTENCE in page,"additional_body":"基督把自己降到最低的地方" in page}
assert all(page_checks.values()),page_checks
sitemap_xml=get("https://ronniecross.com/sitemap.xml")
sitemap=ET.fromstring(sitemap_xml)
locs=[el.text for el in sitemap.findall(".//{*}loc") if el.text]
smatches=[loc for loc in locs if loc.rstrip("/")==link.rstrip("/")]
assert smatches, "previous article canonical link missing in live sitemap.xml"
p=subprocess.run(["gh","run","view","40167360104","--json","status,conclusion,headSha,workflowName"],capture_output=True,text=True)
assert p.returncode==0,p.stderr
workflow=json.loads(p.stdout)
assert workflow["status"]=="completed" and workflow["conclusion"]=="success"
r={"gate":"PREVIOUS_PUBLICATION_PREFLIGHT","result":"PASS","previous_article":TITLE,"previous_article_url":link,"article_id":EXPECTED_ARTICLE_ID,"html_checks":page_checks,"rss_matches":len(matching),"sitemap_matches":smatches,"github_notification_workflow":workflow,"tls":"curl default validated HTTPS; no insecure fallback"}
out=ROOT/"docs/tasks/sermon-philippians-2-12-18-20261101/previous-publication-preflight.json"
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(r,ensure_ascii=False,indent=2))
