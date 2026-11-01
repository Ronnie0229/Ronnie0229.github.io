from pathlib import Path
import hashlib,shutil,json
ROOT=Path(__file__).resolve().parents[3]
SERMON=Path("/Volumes/DevSSD/RonnieWork/RonnieCross/讲道整理")
BATCH="20261101-sermon-philippians-2-12-18-complaining"
KEY="20261101_腓立比书2章12节到18节_从抱怨到发光_Patrick"
PDF="Philippians 2_12-18 Complaining - Google Docs.pdf"
sources=[
 (SERMON/"原始资料/教会讲道"/BATCH/PDF,"fcfbf94c3cd9e66c3c6ba907213435c817a48b132b74ed0d7b27d9de56989839"),
 (SERMON/"英文原稿"/(KEY+".english-source.txt"),"c4748280a08540452f9576f4b8cd3905151d42f306339e52267fbd276a77a61d"),
 (SERMON/"中文原稿"/(KEY+"_中文.txt"),"7e29095e2ecce7ae6f8c924d03b89a60691c599774f7346eaf996299614f1a18")]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
dst=ROOT/"data/raw/教会讲道"/KEY
assert not dst.exists(),f"raw folder already exists: {dst}"
for p,expected in sources:assert p.is_file() and sha(p)==expected,(p,sha(p) if p.is_file() else "missing")
dst.mkdir(parents=True)
for p,expected in sources:
 target=dst/p.name;shutil.copy2(p,target)
 assert sha(target)==expected, target
print(json.dumps({"raw_folder":str(dst),"file_count":3,"sha256":{p.name:sha(p) for p in dst.iterdir() if p.is_file()}},ensure_ascii=False,indent=2))
