Current working-tree native extensions require the next implementation checkpoint:
`ExactSpec.strip_outer_whitespace`, `MathSpec.profile`, and native harness routing.
The existing dependency-pin.patch records the earlier API checkpoint and must be
updated to the actual new commit before distributing this expanded patch. Local
validation currently uses the campaign working tree; no remote availability is claimed.

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

The patch also routes AIW normalization through strict exact, GSM8KPerturbed
through zero-tolerance numeric, and the shared AIME/MATH500 boxed comparison
through math. Missing-parse Minerva fallback and judge prompts remain source-owned.
Further normalization/fallback contracts are described in
[the mapping](../../docs/unification/evalchemy_mapping.md).


The integration requires verifyit implementation commit
`91c55a49599fcdead3475f009e62da4e30ca4f27`, including `math_answer_text`.
Apply `dependency-pin.patch` to declare that exact implementation in the source
project metadata. This commit remains local and unpublished: the remote Git URL
in the dependency patch is a publication target, not an available installation.
Evalchemy's lockfile must be regenerated when that dependency becomes fetchable.
For current validation in an environment with the pinned project's existing
dependencies installed, use the local Git commit and install the patched source
without resolving the unpublished remote dependency:

```bash
uv pip install --python /path/to/environment/bin/python 'verifyit[answer] @ git+file:///path/to/verifyit@91c55a49599fcdead3475f009e62da4e30ca4f27'
uv pip install --python /path/to/environment/bin/python --no-deps /path/to/patched-project
```

An isolated core-only installation from this exact local Git revision was
validated: completed reasoning-only boxes are accepted, truncated reasoning is
rejected, and extracted MCQ choices produce the expected scalar score. No remote
publication or live model endpoint was used.

The GSM8K override retains its version 3.3 extraction/Minerva contract. Its rational
shortcut uses strict verifyit exact on canonical Fraction values; non-rational
answers retain Minerva symbolic scoring. This client hybrid was exposed by real
recorded traces, so it is separate from upstream harness native-config eligibility.
Run the source parity regressions with the patched Evalchemy environment:

```bash
PYTHONPATH=/path/to/verifyit/src:/path/to/patched-evalchemy:/path/to/harness \
  /path/to/evalchemy/.venv/bin/python integrations/evalchemy/check_gsm_override.py \
  /path/to/original-evalchemy /path/to/patched-evalchemy
```
