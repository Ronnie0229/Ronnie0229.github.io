# P5 Website Scripture Parser Targeted Remediation — Independent Read-Only Audit

Audit mode: `SEPARATE_PROCESS / READ_ONLY_SOURCE / COUNTEREXAMPLE_ORIENTED`

Important scope note: this was a separate read-only verification process within the same CodexPro session; it was not a separate LLM context.

Formal verdict:

`PASS_INDEPENDENT_READ_ONLY_AUDIT / MINIMAL_SCOPE_CONFIRMED / EXACT_ZHI_CASE_PASS / EXISTING_FORMS_PRESERVED / GENUINE_CONFLICT_FAIL_CLOSED / ZERO_PRODUCTION_SIDE_EFFECT`

Independent direct source execution confirmed:

- `罗马书12章1至2节` -> `罗马书 12:1-2`
- `罗马书12章1节至2节` -> `罗马书 12:1-2`
- `罗马书12章1节到2节` -> `罗马书 12:1-2`
- `罗马书 12:1-2` -> `罗马书 12:1-2`
- `罗马书12章1节到13章2节` -> `罗马书 12:1-13:2`
- `罗马书12章1节至13章2节` -> `罗马书 12:1-13:2`
- exact P5 body + matching folder/file -> `('罗马书 12:1-2', 'high')`
- genuine conflict folder/file=`罗马书 12:1-2`, body=`罗马书 13:1-2` -> `SystemExit` with `Scripture conflict detected`.

Scope inspection confirmed only the spoken scripture regex in `title_parts()` changed semantically; `resolve_scripture()` conflict detection code was not weakened or removed. No article-id/slug/operation-id special case was introduced.

Frozen artifact readback after remediation:
- successor carrier SHA=`07c11adfead2b98c3143769434f6c1d657c46e7ed71e2725cc727b8001ddaa5b`
- prepublish SHA=`a33f8671ba14131ec58a2975e054181ac8da20d3c74cbf5426507ea346381ad2`
- official_chinese reference SHA=`e91d29548d1d9320927e4a86636eef933dbfac46802cc1ea37deee3916163ca9`
- staged corrected child SHA=`e91d29548d1d9320927e4a86636eef933dbfac46802cc1ea37deee3916163ca9`

Dry-run log inventory contains no operation newer than the already-consumed failed `p5-same-article-shadow-successor-20260911-v1`; no second operation id or dry-run was created.
