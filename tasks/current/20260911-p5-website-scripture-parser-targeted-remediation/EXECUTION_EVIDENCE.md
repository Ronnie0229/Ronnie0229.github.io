# P5 Website Scripture Parser Targeted Remediation — Execution Evidence

Role: `WEBSITE_OWNER / SOURCE_OWNER_STAGE_CONTROL`

Formal execution verdict:

`PASS_TARGETED_REMEDIATION / MINIMAL_SCRIPTURE_RANGE_PARSER_COMPATIBILITY_EXTENSION / DETERMINISTIC_TESTS_PASS / READY_FOR_SEPARATE_READ_ONLY_AUDIT`

## Source diff

Only `scripts/import_sermons.py::title_parts()` spoken scripture pattern changed:

```diff
- rf"(?P<book>{books})\\s*(?P<chapter>\\d+)章(?P<verse>\\d+)节"
- rf"(?:到(?:(?P<end_chapter>\\d+)章)?(?P<end_verse>\\d+)节)?",
+ rf"(?P<book>{books})\\s*(?P<chapter>\\d+)章(?P<verse>\\d+)(?:节|(?=至))"
+ rf"(?:(?:到|至)(?:(?P<end_chapter>\\d+)章)?(?P<end_verse>\\d+)节)?",
```

Semantics:
- existing `到` remains supported;
- `至` is added as the spoken range separator;
- omission of the first `节` is allowed only when immediately followed by `至`, so exact `罗马书12章1至2节` is accepted without broadening arbitrary shorthand forms;
- `resolve_scripture()` conflict gate is unchanged.

## Test chronology

Initial targeted run after only adding `到|至` separator: `FAIL` (1 failure + 1 error), proving exact `1至2节` additionally required the narrow omitted-first-`节` handling. This failure is preserved in chronology.

After the narrow lookahead correction:
- targeted parser regression suite: `5/5 PASS`;
- full Python `scripts/tests` discovery: `55/55 PASS`.

Required deterministic cases:
- `罗马书12章1至2节` -> `罗马书 12:1-2` PASS
- `罗马书12章1节到2节` -> `罗马书 12:1-2` PASS
- `罗马书 12:1-2` -> `罗马书 12:1-2` PASS
- exact P5 body + matching folder/file -> `罗马书 12:1-2`, confidence=`high`, no false conflict PASS
- genuine folder/file `罗马书 12:1-2` vs body `罗马书13章1至2节` -> `SystemExit / Scripture conflict detected...` PASS fail-closed

No Website dry-run or new operation id was created in this remediation stage.
