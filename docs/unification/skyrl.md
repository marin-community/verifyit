# MarinSkyRL verifier mappings

The inventory in [skyrl.json](skyrl.json) pins revision
`91c7a60e85e31b6933ab0ee732125b3338e82b89`. It records 14 registered environments
(13 individual entries and the Nemotron router), 26 Nemotron agent routes, and
9 dormant verifier routes/library scorers. The IFEval registry has 26 checker
names. Each entry names its dispatch, source file/hash, score contract, primitive,
and required adapter. No new verifier category is proposed.

These are adapter mappings, not claims of identical behavior. Executable task
scorers use `script`, `pytest`, or `stdio` for SQL, Lean, grids, calendar constraints,
function calls, and custom numeric comparators. A script that calls retained source
code remains an adapter. The source's XML/CSV OpenAPI validation is stronger than
`xml-elements`/`csv-columns`. Fractional LCB and cohort GenRM require explicit
aggregation adapters. Source extraction must remain at the boundary: first boxed
MCQ, final GSM8K line, and last answer-tag Reasoning Gym have different policies.

`patches/MarinSkyRL/mcq-verifyit.patch` replaces the simplest native comparison
with `grade_mcq_candidate` while retaining first-box extraction and all 26 option
letters. It applies cleanly to the pinned source. The fork must install verifyit
at the integration commit; this patch intentionally does not invent an unpublished
Git dependency pin. Valid prepared tasks retain 0/1 scores. An invalid expected
letter becomes a task error rather than silently producing zero. The patch includes first-versus-last box, lowercase, missing/malformed boxes, and Z
regressions; all 18 source MCQ tests pass in a disposable patched source copy.

AIME's verified correctness is ±1 and its optimization reward also depends on
length/stop evidence. A verifyit 0/1 score must be projected explicitly as `2*r-1`
in the harness, before applying the existing policy. Preserve evaluation budgets,
raw scores, optimization scores, diagnostics, and skipped/unavailable/error states.
Harbor training additionally needs stable per-test IDs, exact stdout evidence, and
completeness for identity-aware shaping; scalar scores alone do not supply this.

## Recent patch coverage

| Source patch | Edge case | verifyit counterpart evidence or remaining requirement |
|---|---|---|
| `00fcf63` | stdin byte reads | Added `test_stdio_binary_stdin_program_scores_correct_output`; real subprocess passes. |
| LCB/coder1 runtime handling | correct stdout before crash | Added parameterized `test_stdio_correct_output_before_candidate_crash_scores_zero`; both normal and special-judge paths failed before fix, pass after. |
| `22e5bc0` | exact rational AIME value | Existing `test_math_scalar_answers_are_compared_symbolically` covers .5 versus 1/2; the exact rational boundary adapter also covers large-decimal policy, avoiding symbolic broadening. |
| `aa86ee3` | ASDiv integer ratios | Source rational ratio normalization must occur before primitive call; `test_aime_normalized_answer_exact_rational_equivalence` covers equivalent/reversed ratios, zero denominators, huge decimals, and rejected candidate syntax; 17 arithmetic adapter cases pass. |
| `5a7ede7` | standalone final GSM8K line | Numeric last-number extraction is different; `test_gsm8k_requires_exact_value_on_standalone_final_line` covers prose-tail, malformed comma, multiple markers, and exact huge decimals. |
| `0cdccc9` | first boxed MCQ and options >4 | `test_mcq_fifth_option_is_gradable_when_declared` and candidate helper tests cover core range; patched source tests cover first-box extraction and options through Z; all 18 pass. |
| `400f598` | JSON grid and unfenced transforms | Structural parsing/execution adapter required; generic exact mode cannot prove palette/rectangular validation. |
| `cdc6600` | truncated math judge retry with larger budget | Source two-call retry policy must remain explicit; core judge local HTTP tests do not prove this adapter policy. |
| `fc65842` | binary code short circuit | stdio stops at first failure and existing first_failure/passed tests cover counterpart; functional adapter and fractional mode still need tests. |
| `196143f` | Snowball reasoning stripping, bounded chat output | Provider/harness evidence extraction remains outside string primitive; add boundary tests. |
| `a5df364` | Ultra configuration versus candidate failures | Core verdict statuses cover distinction; each Ultra script must map schema/registry failures to unscored states. |
| `24d567f` | verifier child memory/total timeout | stdio timeout coverage exists; memory/output bounds and functional child parity remain adapter work. |
| `5beb28c` | jailbreak judge examples/verdict format | Custom YAML prompt/parser adapter coverage required. |
| `d8b6e8c` | skip grading while preserving tools/Lean refinement | Harness state contract; no deterministic score should replace skipped/unavailable. |
| `91c7a60` | prepared GSM8K/preference extras | Boundary row normalization required; preference remains external reward model. |

Candidate nonzero exits now score zero in stdio, even with correct stdout. The
19 stdio tests pass. Existing task-supplied special judge crashes/timeouts still
reject candidates, and unavailable command paths still score zero by current
contract; infrastructure classification for those boundaries needs a separate
review before changing it.

`arithmetic-verifyit.patch` routes source-normalized AIME answers and GSM8K final-line
answers through the exact rational adapter. Strict-box extraction and AIME reward
shaping remain in the harness. All 40 source AIME/GSM8K tests pass after applying
the patch to a disposable copy; both patches apply cleanly to the pinned revision.
