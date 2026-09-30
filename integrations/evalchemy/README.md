The patch targets marin-community/evalchemy
`e3f4a3d601896c437f37b0bd0a30e51651cce6d0`.
Install verifyit in the evaluation environment and apply `verifyit.patch` from
the Evalchemy checkout. Apply the separately pinned harness patch to its installed
harness dependency for native tasks.

GPQA Diamond and MMLU-Pro retain their answer extraction and aggregation. Their
extracted option letters now call verifyit's `grade_mcq_candidate`; GPQA declares
four options and MMLU-Pro ten. Category and repeat counts, standard errors and
sample records remain Evalchemy-owned.

The shared extraction boundary calls verifyit's completion adapter. Final content
takes precedence over reasoning; completed reasoning-only math answers require a
box, while truncated reasoning-only output supplies no answer. Inline reasoning
end markers are handled before benchmark box extraction. The patch retains the
benchmark's own box parser and stop-sequence handling.

This patch does not replace mathematical equivalence or judge prompts. Their
normalization/fallback contracts require additional parity work described in
[the mapping](../../docs/unification/evalchemy_mapping.md).
