# Verification — S4 Malformed Provider Status Type-Safety Closure

正式 verdict：`PASS_S4_MALFORMED_STATUS_TYPE_SAFETY_CLOSURE / READY_FOR_FRESH_INDEPENDENT_AUDIT`

## Required malformed-status matrix

All cases below now produce bounded terminal fail-closed with no raw implementation exception:

- dict: `{"nested":"DICT_STATUS_MARK"}`
- list: `["LIST_STATUS_MARK"]`
- nested dict/list mixture with unique marker/body
- numeric status
- boolean status
- null status
- tuple structured status
- unknown string status

For every case:

- raw terminal classification => `PROVIDER_RESULT_STATUS_INVALID`
- durable Website status => `TERMINAL_FAIL_CLOSED`
- provider diagnostic evidence => `{}`
- artifact calls => 0
- serialized durable JSON malformed marker/body => absent
- execution owner after durable fail-closed => absent
- `status()` read => normal terminal status + last_error
- `result()` read => terminal status + empty provider_result + artifact null
- terminal reconcile => ready=0 / speech=0 / artifact=0

## Test chronology

Initial py_compile after implementation => PASS.

Initial runner after adding malformed matrix => `54 tests / 8 errors`.

Those 8 errors were test-surface errors only:
- test expected `result()["last_error"]`
- existing formal result surface intentionally exposes status/provider_result/artifact, while `last_error` is exposed by `status()`
- malformed provider jobs had already durably reached the required fail-closed outcome

Test correction stayed inside current write-set and did not alter product semantics.

After correction:
- runner => `54/54 PASS`
- full Website Python => `115/115 PASS`

After nested/tuple body marker strengthening, final rerun:
- `python3 -m py_compile scripts/read_aloud_s4_runner.py scripts/tests/test_read_aloud_s4_runner.py` => PASS
- runner => `54/54 PASS`
- full Website Python => `115/115 PASS`

## Regression matrix

Existing semantic persistence, execution, stale-owner, authorization claim, render binding, artifact SHA, UNKNOWN reconcile, terminal reconcile regressions all remain PASS in final runner suite.

## Hygiene / runtime boundary

Final checks:

- production runtime root => `False`
- malformed-status task temp leftovers => `[]`
- durable-runner implementation test temp leftovers => `[]`
- trailing whitespace scan => PASS
- space-before-tab scan => PASS
- EOF newline scan => PASS

Current CodexPro connector policy forbids bash Git diff/status inspection. Literal `git diff --check` was therefore not bypassed; `show_changes` + whitespace/EOF equivalence is used here, leaving literal rerun to fresh independent Auditor if its environment permits.

## Side-effect boundary

Pilot remains `UNCLAIMED / NOT_CONSUMED`; no real provider POST, production runtime, LaunchAgent, audio, external mutation, R2/NAS/deploy, commit or push.
