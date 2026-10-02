---
name: audit-preparation
description: Independently classify added structural conversion and policy preparation functions before integration acceptance or publication.
---

# Audit preparation

Use an independent clean-room agent that has not participated in the implementation
or read its intended safety classifications. Give it the actual frozen diff,
source contracts, supported input examples, and current primitive APIs.
Do not supply the author's intended answers or preferred classification.

Inventory every added structural-conversion and policy-preparation function,
including new shared helpers, with its source location and frozen revision/hash.
For each function, the auditor must:

- Classify **safe** only when conversion preserves the information and semantics
  required by the declared grading contract. Otherwise classify **unsafe** and
  identify how it can affect grading. These labels do not establish security.
- Read actual implementation and relevant callers, not only annotations or tests.
  Review current primitives for duplicated extraction, normalization,
  matching, or policy operations and identify reuse opportunities.
- Explain whether an unsafe conversion can be made safe, and how, when possible.
  If its grade-affecting behavior is intentional, require an explicit named policy,
  source-preserving default, and effective policy provenance.
- Check that preparation failures cannot reach grading as successful partial data.

Keep the per-function findings and inspected hashes in the external task artifacts.
Every added function must have a disposition before acceptance or publication;
resolve defects, obtain focused re-review after behavior changes, and retain
unresolved scope explicitly. Unsafe classification is not itself a rejection:
reviewed policy composition can be supported with actual end-to-end evidence.
Safe conversions need unit coverage; composed safe/unsafe stages need actual
client-path tests under [test-integration](../test-integration/SKILL.md).

Agents enforce this gate. A cheap static inventory or boundary check is useful
when it catches real omissions, but it cannot certify semantic safety or replace
independent inspection. Do not build an audit framework solely to track this gate.
