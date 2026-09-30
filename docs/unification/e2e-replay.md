# Recorded trace replay

The Evalchemy and lm-eval-harness cutovers replayed all recorded samples from
three randomly selected validated model-run links for each of eight benchmarks.
The selection was frozen before downloads or scoring with seed 20260930 and
SHA256 `575523245c2f131685e749edf0d3a546f96cadc4566425eacb4543078405e64a`.
All 24runs reproduced 63,360sample scores with zero mismatches and 68,913actual
verifyit primitive calls. Every deterministic point metric matched the precise
archived score, and every primary score matched the rounded tracker value.

| Benchmark | Runs | Samples per run | Scoring route |
| --- | ---: | ---: | --- |
| PIQA | 3 | 1,838 | Harness likelihood-choice through MCQ; raw and normalized accuracy |
| Winogrande | 3 | 1,267 | Harness likelihood-choice through MCQ |
| BoolQ | 3 | 3,270 | Harness likelihood-choice through MCQ |
| GSM8K zero-shot | 3 | 1,319 | Evalchemy override; canonical rational exact with symbolic fallback |
| MATH500 | 3 | 500 | Boxed math with explicit missing-parse source fallback |
| AIME24 | 3 | 300 (30 problems × 10 repeats) | Boxed math with explicit missing-parse source fallback |
| GPQA Diamond | 3 | 594 (198 problems × 3 repeats) | Source answer extraction, verifyit MCQ |
| MMLU-Pro | 3 | 12,032 | Source answer extraction, verifyit MCQ |

This is a scoring/filter/aggregation replay. Harness runs the actual
`lm_eval.evaluator.evaluate` entrypoint with recorded responses returned at the
LM boundary. Request documents and choice continuations are checked against the
recorded inputs. Custom runs execute actual source extraction and Evalchemy
`_score_custom_task`; immutable recorded documents supply prepared benchmark
state instead of downloading datasets. No scorer is mocked. Core profiling
records actual callable, module, spec, candidate and Reward. Harness bootstrap
stderr is omitted; deterministic point metrics and every sample are compared.
The replay does not claim regenerated inference, identical prompts, or runtime
coverage of the entire 13,982configuration inventory.

AIW, GSM8KPerturbed and AIME25 have no validated links in the supplied tracker.
Their missing traces remain explicit rather than being counted as passed.

## Trace-exposed mapping correction

The initial GSM run used upstream harness version 3.0. An unmodified baseline
reproduced its mismatch with archived flexible-extraction scores. The recorded
campaign uses Evalchemy override version 3.3, including its final-answer filter
and Minerva equivalence. The client now routes the source rational shortcut
through strict exact equality on canonical Fraction strings; missing extraction
returns verifyit scored zero and non-rational cases retain source symbolic
scoring. This is a hybrid integration, not native symbolic equivalence.

Eight tracked source-parity cases cover `28.00` versus `28`, equivalent fractions,
rational mismatches, missing extraction, symbolic equality/mismatch and scorer
error propagation. The patch applies to pinned Evalchemy without changing core
verifyit. All three corrected GSM runs match every sample and both strict and
flexible metrics. The upstream 10,841native-config eligibility count is unchanged.

## Evidence and reproduction

Campaign evidence is outside Git at
`/Users/benfeuer/Documents/experiments/active/verifier-unification/evidence/e2e/evals`.
Raw traces and credentials are not repository artifacts. The catalog and source
manifest preserve exact provenance rather than relying on mutable paths:

- `selection.json`: complete candidate population, tracker hash and frozen links.
- `downloads/*/*/provenance.json`: immutable archive manifests and blob hashes.
- `catalog.json`: per-run counts, score comparisons and report hashes.
- `source_manifest.json`: framework/core revisions, working-diff and source hashes.
- `replays/*/*/native`: command, stdout/stderr, framework report and primitive calls.
- `superseded/upstream-gsm8k`: original misrouting and unmodified baseline.
- `manager-piqa`, `manager-math500`, `manager-gsm`: independent successful reruns.
- `evidence_index.json`: hash index for replay evidence.

From the campaign verifyit worktree:

```bash
PYTHONPATH=$PWD/src:../framework-worktrees/evalchemy:../framework-worktrees/lm-eval-harness:../scratch/evalchemy/deps \
  /Users/benfeuer/Documents/evalchemy/.venv/bin/python \
  ../evidence/e2e/evals/replay_harness.py gsm8k-0shot 0 --output /tmp/gsm-replay
```

Use `replay_evalchemy.py math500 0` for custom scoring. The output override
preserves original evidence. `build_catalog.py` regenerates aggregate comparisons.
The tracked [GSM source parity check](../../integrations/evalchemy/check_gsm_override.py)
accepts original and patched Evalchemy roots and runs with their real optional
scoring dependencies. The integration retains verifyit[answer] and its required
math-verify minimum; no unpublished remote installation is claimed.

## Other framework replays

The [SkyRL replay report](skyrl.md) records 66 actual full-trajectory executions:
all 66 match the pinned native verifier, and 65 match the archived producer score.
The remaining case (`045` versus `45`) is source drift: the producer used literal
string equality, while the pinned source added rational equivalence. Its archived
negative score is preserved, and the pinned-source behavior has a regression.
The arithmetic patch also passes 14 actual framework GSM tests.

The [Harbor replay report](harbor_replay.md) records three separately frozen Tau3
model runs containing 1,101 final trials: 1,051 equal numeric scores, 37 originally
unscored trials recovered as valid zero, ten remaining infrastructure failures,
and three database discrepancies where fresh native replay also returns zero.
The three discrepancies are preserved; archived parity is not claimed. Its ScriptSpec bridge retains native evaluator
metrics while checking pinned runtime assets before scoring. Tampering produces
infrastructure-error zero; three real clean positive cases cover Telecom,
Retail and BankingNL. These checks prevent modified runtime databases from
silently producing positive rewards.

Final integration verification passed 492 tests with one absent-Go-toolchain skip,
required Ruff/Black/Pyrefly checks, package build and local documentation links.
No core grading change was required by these replay findings; changes are client
integration, asset protection, source parity regressions and documentation.
