# MarinSkyRL integration

Source pin: `91c7a60e85e31b6933ab0ee732125b3338e82b89`. Apply the MCQ and
arithmetic patches, then the dependency pin patch. The latter pins the local
verifyit implementation checkpoint and raises the standalone gym Python floor
to >=3.11. A later implementation checkpoint may be required when this campaign
lands additional APIs; the source SHA must exist on the remote before external
installation. Do not silently replace a pinned Git dependency with a floating
branch. Regenerate fork locks in the fork's supported environment before use.

The MCQ patch retains source strict first-box extraction, signed reward and
length shaping, and calls verifyit only for candidate correctness. Arithmetic
patches retain source AIME rational equivalence and GSM8K final-line equality;
the multi-turn GSM8K adapter is specified separately and is not implemented by
the final-line helper. Patched source regressions and verifyit API regression
counts are recorded in [the mapping](../../docs/unification/skyrl.md).
