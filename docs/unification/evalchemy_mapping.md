# Evalchemy mapping

Source: marin-community/evalchemy
`e3f4a3d601896c437f37b0bd0a30e51651cce6d0`.
[The generated inventory](evalchemy_inventory.json) covers all 42 custom benchmark
classes discovered by the repository's `*/eval_instruct.py` dispatch convention,
22 local harness YAML overrides and 72 scoring entry points. Discovery indexes
all 4,261 Python definitions under `eval/` in transient evidence, including
normalization helpers whose names do not contain `grade` or `score`. Each record carries source path/hash, inheritance, declared metrics,
scoring calls where defined, primitive candidate, and explicit parity caveats.
Unknown custom benchmark additions fail regeneration rather than silently mapping
to `script`. Static imports and function references are evidence for follow-up;
dynamic dispatch still requires runtime verification.

| Benchmarks | Primitive candidate | Score contract / remaining work |
| --- | --- | --- |
| GPQADiamond, MMLUPro | `mcq` after source extraction | Implemented patch calls `grade_mcq_candidate`; preserve source option shuffle, categories, repeat vectors and standard errors |
| AIME24, AIME25, AMC23, HMMT, MATH500, JEEBench | `math` | Box extraction and anchors/fallback equivalence need parity; JEE includes mixed numeric responses |
| OlympiadBench, OlympiadBenchFull, OlympiadBenchDeterministic | `math`, with source judge policy | Preserve deterministic versus judge-fallback distinctions and units; do not add a judge to deterministic variant |
| GSM8KPerturbed, AIW | `exact` with source normalization | Strict extraction differs from raw verifyit file normalization; unresolved parity |
| IFEval | `ifeval` | Preserve strict/loose prompt and instruction aggregates; instruction registry parity unresolved |
| IFBench | `script` with original registry | Expanded instruction catalog should remain data/plugin orchestration until shared checker equivalence is shown |
| CodeForces, CodeElo | `stdio` candidate | Preserve case aggregation, tolerances, compilation outcomes, timeouts and contest orchestration |
| HumanEval, HumanEvalPlus, MBPP, MBPPPlus, BigCodeBench | `script` hosting source tests; `pytest` candidate where representable | Preserve sanitization, indentation fixes, execution outcomes and pass@k; avoid collapsing infrastructure failures into wrong answers |
| LiveCodeBench, LiveCodeBenchv5, LiveCodeBenchv5_official | `script` / `stdio` candidate | Shared bounded grader has function-call and stdin contracts; preserve per-case result labels and timeout cleanup |
| MultiPLE, SWEbench | `script` hosting task toolchain | Language execution or repository harness belongs with task; retain tests and container setup |
| CruxEval | `script` | Preserve directional input/output checks and sample records |
| SimpleQA, SimpleQAMini, FinanceBench, HLE | `judge` candidate | Exact prompt/label/retry behavior, not-attempted labels and judge errors need parity; SimpleQA conditional accuracy/F1 cannot be discarded |
| MTBench, WildBench, alpaca_eval, MixEval | `judge` candidate | Multi-turn/pairwise ranking, reference selection and score scales remain benchmark-owned |
| MRCR | `script` | Preserve reference-prefix matching, response comparison score and trial records |
| NUPA-Loose, NUPA5K-Loose | `script` | Exact-match, digit-match and format-validity metrics have distinct denominators; numeric tolerance is not equivalent |
| RepoBench, LiveBench, zeroeval | `script` with source metric bridge | Multiple scorer families and task routing require per-family parity; callable index links their scoring functions |

The [Evalchemy integration patch](../../integrations/evalchemy/README.md) replaces
GPQA/MMLU letter equality with verifyit candidate scoring while retaining source
extraction and all aggregates. Source method execution before/after the patch
produced identical outputs for correct, wrong and missing choices, categories and
repeat metrics. Both integration patches apply cleanly to pinned checkouts, and
patched Python parses. The actual upstream AIME24/AIME25, MATH500 and MMLU-Pro
regression suites pass against the patched validation tree: 26 tests, including
provider completion fields and persisted sample records. The metric bridge for native tasks preserves the source
scorer; this does not establish primitive equivalence for unresolved rows.

Recent patches reviewed and regression consequences:

- `bafdd55` (#186): MMLU-Pro final content overrides tentative reasoning and
  lower-case extracted choices normalize to upper-case. Completion adapter tests
  exercise final precedence and inline reasoning end markers through MCQ scoring.
- `7920acf` (#185): completed reasoning-only math may supply a boxed answer;
  length-truncated reasoning may not. Completion adapter tests cover both and
  final-content precedence. The fork patch retains the source box parser/stops.
- `e80fc88` (#170) and `5becb4e` (#174): mathematical representation equivalence
  and final-answer extraction. Verifyit anchors with `$...$`, whereas Evalchemy
  boxes parsing and falls back to Minerva string normalization; parity remains
  unresolved and is not claimed by the completion tests.
- `9447eed` (#148): indented Plus code and generation limits are task extraction /
  orchestration concerns. Source-hosted test execution must retain dedentation.
- `791d41c` (#150): common bounded LiveCodeBench grader preserves code test case
  outcomes and timeout cleanup. Future `stdio` migration must cover function-call
  cases before replacing the original script.
- `b102201` (#145), `08bcaae` (#144): judge/execution failures remain separate
  trial records; metric projection never turns these records into candidate zero.

No additional verifier category is proposed. The implemented reusable gaps are a
provider completion boundary and a metric-preserving bridge, both independent of
benchmark dependencies. Remaining candidate mappings need parity work before a
fork can remove its original scorer.
