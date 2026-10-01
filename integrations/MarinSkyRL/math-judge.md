# Math and symmetric judge integration

`math-judge-verifyit.patch` applies after `instructions-verifyit.patch` at MarinSkyRL
`91c7a60e85e31b6933ab0ee732125b3338e82b89`. Apply `dependency-pin.patch` last.
The dependency is verifyit `eaa768d773885c597c03e708690b57034490ba91`, using its
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

`math-reference-contract-verifyit.patch` follows the instruction preparation
patch in the cumulative integration stack. The three public Nemotron source
builders accept `math_reference_kind="semantic"` or `"symbolic"`, or preserve an
explicit kind already present in the trusted source row. This choice is serialized
before candidate generation. Conflicting or malformed kinds fail preparation.

Semantic references require nonempty, transport-valid question and answer text;
they use the original symmetric judge directly, without guessing a mathematical
meaning from the answer's spelling. Unicode punctuation, multiline prose and TeX
text are allowed. Symbolic references require the parsed mathematical contract;
a parser miss cannot silently switch them into semantic judging. Empty references
and malformed metadata return invalid-task zero before judge calls.

For untagged legacy records, trusted reference validation precedes candidate gating. Parsed mathematical
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

These remain partial integrations for the full legacy source population. Prepared
semantic and symbolic contracts are integrated, but untagged references outside
the bounded legacy domains still need an explicit trusted contract selection.
No backward compatibility for arbitrary untagged references is inferred.

Thirty-seven math source tests and nine instruction preparation regressions pass.
Sixteen prepared source/Env roundtrips cover both routes and all three builders,
including positive and negative semantic and symbolic answers. Native and cutover
scores and HTTP requests match. The manager independently checked the roundtrips;
the same cases pass with the exact installed verifyit revision and fresh exported
source stack. Evidence and the 22-patch provenance manifest are in
`evidence/e2e/wiring/skyrl-math-reference-contract/`.

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
