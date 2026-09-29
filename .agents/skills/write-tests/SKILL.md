---
name: write-tests
description: Add, revise, or review verifyit tests for an explicit behavior change, regression, or test-quality request.
---

# Write tests

Read root AGENTS.md, CONTRIBUTING.md, and TESTING.md. They own behavioral value,
test style, fakes and mocks, timing, numerical tolerances, and commands.

Before adding a standalone scalar or configuration guard test, name the
reported regression or public contract it protects. Otherwise test the
consequential behavior on the valid path or omit the test. Do not pin a dependency
version, default, or serialized configuration unless a consumer depends on it.

Extend the existing mode test file. Prefer real temp workspaces, subprocesses,
and the local judge HTTP fixture to mocks of internal helpers. Run focused
tests while editing and the full local suite for behavior changes before publication.
