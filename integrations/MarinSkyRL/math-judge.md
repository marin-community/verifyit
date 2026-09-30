# Math and symmetric judge integration

`math-judge-verifyit.patch` applies after `instructions-verifyit.patch` at MarinSkyRL
`91c7a60e85e31b6933ab0ee732125b3338e82b89`. Apply `dependency-pin.patch` last.
The dependency is verifyit `67db341c77449f0977bb034c6d7fca034038b98f`, using its
`answer` and `judge` extras. The optional judge SDK requires OpenAI >=1.59.9.
Local installation from this exact implementation commit was tested; remote
publication of that commit is not claimed.

The opt-in `verifyit_enabled` dispatch covers math-with-judge and NS-tools terminal
math scoring. Existing source NS-tool sessions continue to execute in the actual
NeMoSandbox runtime. The terminal checker uses existing MathSpec RAW extraction,
finite scalar additive equivalence and JudgeSpec configured final labels inside
a ScriptSpec process group. `verifyit_math_total_timeout_seconds` bounds the full
checker (default 60 seconds); child inputs and reports remain in the owning host
temporary directory, which is removed after normal completion or timeout.

Source final-answer extraction and pure-expression gating remain client behavior.
Ordinary mathematical references use the source boxed-LaTeX reference extraction
and unwrapped expression/LaTeX prediction extraction. Indefinite integral questions
permit only a finite additive scalar difference after ordinary equality fails.
This deliberately removes source false positives from constant set/interval
differences and nonfinite differences. Equations and matrices do not use additive
fallback. Original parsed objects determine correctness; source stringified
extraction diagnostics remain metadata.

Trusted reference validation precedes candidate gating. Parsed mathematical
expressions retain symbolic scoring even when their spelling resembles words.
References yielding only strings may use the judge when they belong to a bounded
natural-language domain: Unicode letters/digits, spaces and ordinary sentence
punctuation, with a multi-letter word and no reserved mathematical constant.
Known paired TeX sizing commands can be removed solely to validate a reference
that the original extraction cannot parse; such a reference retains the source
judge fallback. Its original spelling is preserved in the prompt. Unbalanced
braces/sizing pairs, unknown unparsed mathematical syntax and empty references
are invalid tasks. Actual parsing/checker errors are infrastructure failures;
they cannot retain credit or become positive judge fallback.

The symmetric judge performs the original two orientations with the original
trusted source system/user prompts, temperature 0, token budgets 8192/16384 and
optional reasoning effort. Completed reasoning blocks are stripped before label
parsing. Each final label is exactly `[[A=B]]` or `[[A!=B]]`; contradictory answer
labels, refusal/tool fields, malformed completions and HTTP errors invalidate
the composition with zero reward. Only length truncation permits one larger
budget. HTTP retries are disabled for this rubric. A failure in the second judge
discards any first-judge positive credit. Full archived external judge text is
retained in diagnostic metadata.

These are partial integrations. They do not claim arbitrary natural-language
references or all mathematically valid but parser-unsupported reference syntax.
The remaining domain needs an explicit trusted reference representation or
further reviewed syntax validation; an arbitrary parser miss must not become
unrestricted positive judge fallback. The comprehensive pending register retains
both source routes.

Twenty-five source before/after and failure-boundary tests pass. They include
plain symbolic names, typography-only references, positive/negative symmetric
judge requests, malformed trusted references independent of candidate form and
backend failure that must not reach a positive judge. The core checkpoint passed
155 focused tests and 760 full-suite tests (one Go skip).

The full real-trace population contains 294 verified links in six benchmark groups.
Three seeded selections per group were frozen before scoring, producing 18 actual
Env roundtrips. Sixteen match recorded and pinned-native score and framework
reward. Two NS-tools items lack archived external judge transcripts and remain
explicitly incomplete; both native and patched replay fail closed with zero
framework reward, without inventing responses or resampling. The manager
independently reran the repaired prose and typography cases and the 25 source
tests. Evidence, input hashes, local HTTP transcript transport and rerun driver
are under `evidence/e2e/wiring/skyrl-math-judge/`. Historical RAW/reference-routing
discrepancies remain separate from `patched-final/`.
