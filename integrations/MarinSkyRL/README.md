# MarinSkyRL client integration

Framework routing remains opt-in. Installing verifyit does not patch SkyRL,
change its dependency lock, or enable grading through verifyit.

The client uses the existing Exact, Math and Judge modes and retains source
scorers where their contracts require a runtime. Direct Judge calls use
`grade_judge_candidate` with runtime-only `JudgeConnection` credentials.
`call_bounded` enforces a total process deadline and cleans up child processes.
Use a verifyit revision containing those APIs; older deployed pins lack them.

Source-specific patches, pinned application order and replay receipts are
campaign artifacts outside this package. The local campaign checkout stores
patches and their original application guide at `artifacts/MarinSkyRL/`.
They are not downloaded or applied by verifyit, and no public artifact hosting
is implied. See [artifact availability](../../docs/unification/README.md).
