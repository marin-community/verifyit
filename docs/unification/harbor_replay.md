# Harbor recorded-trace replay

The replay selects three completed tau3 model-run links from the seven linked in
`eval-policy-09-25/TRACKER.md`, before scoring, with seed `2026093001`. The selected
runs are Qwen3-Coder (recorded rounded mean 0.083), gpt-oss-20b (0.067), and Gemma4
(0.018). All saved final trials are included; retries are selected using each
recorded result's final attempt path. The complete populations, selection,
tracker SHA256, object sizes, and input hashes are retained in the campaign's
`evidence/e2e/harbor/` directory. No trace samples are compared to run aggregates.

The driver executes the actual patched Harbor `Verifier` and `DockerEnvironment`,
which invoke installed verifyit in a real container, then the retained tau3
native evaluator and pinned tau2 runtime. Task sources are restored from dataset
commit `3bdba90fbd922e9257c0ec16067c5a16626e612f`; all 375 task evaluator files
match the pinned bridge's retained native source byte for byte. The image uses
verifyit `739d765d89ec1d36df0e16111c28e85d1f0f2a92` and tau2
`fc0055dc4e0a316c3f83133267fbd6faaa770992`. Native assertions use real recorded
messages and real configured judge calls. No simulated environment or judge is
counted as replay evidence.

The original aggregates exclude unscored trials: Qwen has 375 scored of 375,
gpt-oss has 341 of 357, and Gemma has 338 of 369. The final replay report records
that original denominator separately from an all-trial mean with errors at zero.
An original infrastructure error becoming a valid zero is reported separately
from a numerical score mismatch.

One real mismatch exposed mutable grader assets: Gemma's airline-11 trace wrote
an exact recorded script modifying the native base database. The saved runtime
contains dialogue but no corresponding native mutating tool calls. Fresh native
replay and verifyit both return zero; executing the saved script in an isolated
container reproduces the original polluted native one. This diagnostic one is
not counted as correct parity. The client now generates a trusted asset hash
manifest from pinned Git objects and checks it before grading. The same real
mutation now produces `infra_error`, reward zero, and no scalar reward file.
Three further hardened Docker cases, one from each selected run, retain genuine
positive rewards, including telecom, banking knowledge, and a retail task whose
reward basis includes native natural-language assertions.

The remaining seven tracker Harbor benchmarks were also inspected. Five public
pinned representative task scripts lack native verifyit specs; TerminalBench2
and SOTOPIA record local/cache source paths requiring their dataset provenance.
OT-TBLite's pytest runner is a plausible native pytest client route, while
SWE-bench needs restored repository patches/protected test identities. DS1000,
BFCL, and BixBench retain custom graders. Representative archived artifact
listings contain no complete candidate workspace snapshots. These are remaining
client/artifact requirements, not successful native cutovers. A generic Harbor
dispatch hook alone does not establish executable native coverage.

All **1,101 unique final trials** completed the frozen 739d765 replay. The catalog
checks exact saved runtime bytes, final-attempt identities, retained native
source, the frozen bridge, image identity, installed package file hashes, and
reward-file/status consistency. It reports 1,051 equal recorded scores, 37
originally unscored trials now producing valid zero, 10 still unscored with
infrastructure errors, and three native database mismatches. Fresh native Docker
controls also return zero for both retail mismatches; their original modified
workspace state remains unavailable. No judge-only score mismatch was observed.

| Run | Original scored / total | Original mean over scored trials | Replay over the original scored denominator | Replay over all trials, errors zero |
| --- | ---: | ---: | ---: | ---: |
| Qwen3-Coder | 375 / 375 | 0.082666667 | 0.082666667 | 0.082666667 |
| gpt-oss-20b | 341 / 357 | 0.067448680 | 0.067448680 | 0.064425770 |
| Gemma4 | 338 / 369 | 0.017751479 | 0.008875740 | 0.008130081 |

The three Gemma positive-to-zero changes agree with fresh native controls;
one is proved to depend on grader-database contamination. They are not counted
as archive matches. The separately tested asset guard was not mixed into the
full frozen replay: three clean positive cases and the genuine contamination
case validate its new boundary. This report does not claim that all 87 Harbor
adapters have deployed parity.
