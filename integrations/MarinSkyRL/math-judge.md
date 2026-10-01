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

Apply `math-hybrid-reference-verifyit.patch` after `coder1-protocols-verifyit.patch`
and before the dependency pin. Untagged legacy rows use the pinned source's fixed
hybrid policy: nonempty transport-valid reference text, an optional symbolic
shortcut, then the actual symmetric semantic judge. Ordinary parser rejection
does not invalidate an otherwise valid textual reference. Unknown TeX macros and
multiline prose remain text contracts. Explicit symbolic contracts still reject
unparsed references. Raised parser failures return unscored zero and never
become positive judge fallback. Reference policy does not depend on the candidate.

The symmetric judge performs the original two orientations with the original
trusted source system/user prompts, temperature 0, token budgets 8192/16384 and
optional reasoning effort. Completed reasoning blocks are stripped before label
parsing. Each final label is exactly `[[A=B]]` or `[[A!=B]]`; contradictory answer
labels, refusal/tool fields, malformed completions and HTTP errors invalidate
the composition with zero reward. Only length truncation permits one larger
budget. HTTP retries are disabled for this rubric. A failure in the second judge
discards any first-judge positive credit. Full archived external judge text is
retained in diagnostic metadata.

Both terminal-scoring routes are integrated and validated. Forty-seven source
regressions pass, including unexpected parser failures, malformed contracts and
judge transport failures. Twelve source/Env fixtures cover legacy prose, unknown
TeX and explicit symbolic references with positive and negative answers. Native,
cutover, independent manager and exact installed-package scores and HTTP requests
match. The 24-patch manifest proves fresh-stack source byte equivalence.

The real-trace population contains 294 verified links in six benchmark groups.
The original three seeded selections per group remain frozen: all 18 now match
recorded and pinned-native scores and framework rewards. The two NS-tools judge
transcripts previously reported missing were present under nested multi-turn
diagnostics; the replay extractor was wrong. Corrected transport matches exact
source prompts to those archived responses, with no generation or resampling.
Original failed evidence is preserved and superseded by
`evidence/e2e/wiring/skyrl-math-transcript-correction/`, including independent
manager and exact installed-package reruns. NS tool execution remains in the
source runtime; this validates terminal grading, not sandbox execution itself.
