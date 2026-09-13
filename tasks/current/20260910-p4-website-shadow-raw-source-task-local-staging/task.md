# task｜P4 Website Shadow Raw Source Task-Local Staging

日期：2026-09-10

正式角色：`WEBSITE_OWNER`

状态：`PASS_STAGE_TERMINAL`

## Upstream preserved truth

- candidate/official_chinese SHA=`b4ce3d9d93f89dd341f6ab75ff2a4b13df1d74875b4495a0edba06998250316a`
- prepublish SHA=`c112f552ad6ff25dee5553473078353b87480dfdf15338fb7ef75743971d96bf`
- fidelity_status=`independently_verified`
- Human Gate=`PASS / P4_SHADOW_DRY_RUN_ONLY`
- B-min=`MECHANICAL_PRESENTATION_PASS`
- production_publish_authorized=false

## Exact staging

Website raw folder:

`data/raw/教会讲道/20260910_罗马书12:1-2_心意更新与日常服事_Patrick`

Staged source file:

`20260910_罗马书12:1-2_心意更新与日常服事_Patrick_中文.txt`

The staged file is a byte-for-byte copy of the current Sermon Owner `official_chinese.txt` and retains SHA-256:

`b4ce3d9d93f89dd341f6ab75ff2a4b13df1d74875b4495a0edba06998250316a`

The original suggested filename using `罗马书12章1-2节` was not retained because current importer filename scripture parsing reduced it to `罗马书 12` and caused a scripture conflict. The final filename uses the current importer-compatible `罗马书12:1-2` form without changing file bytes.

## Preflight

Current `scripts/import_sermons.py --folder <folder> --dry-run` was executed with the already-approved description and precise non-generic tags. Final preflight PASS:

- folder parsed
- source file parsed
- scripture=`罗马书 12:1-2`
- title=`罗马书 12:1-2｜心意更新与日常服事`
- Would import=`1`
- Skipped=`0`
- Dry-run=`no files written`

## Forbidden

No processed/post/registry write; no fixed publication dry-run; no build/publish/push/deploy/notify; no P5/production; no Git commit/push.
