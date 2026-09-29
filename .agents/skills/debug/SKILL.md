---
name: debug
description: Diagnose a stated verifyit grading, parsing, CLI, dependency, or executable-test failure.
---

# Debug

Read AGENTS.md, CONTRIBUTING.md, and TESTING.md. Keep working notes in the
active task or existing issue/PR. Search Git history and related GitHub issues
when prior behavior could explain the symptom.

Reproduce with the smallest spec, candidate output, and local workspace that
shows the failure. Identify whether the observable outcome is a wrong score,
invalid task, infrastructure error, or an incorrect CLI/verdict file. Trace
through spec parsing, grade dispatch, the mode grader, and shared execution
helpers as needed.

Keep optional-dependency installation and task-toolchain failures distinct
from candidate failure. Use the local HTTP fixture for judge diagnosis unless
a live endpoint is explicitly part of the requested work. For subprocess
failures, inspect exit status, timeout state, stdout/stderr, and process-group
cleanup in a temporary workspace.

State a falsifiable cause, change one cause at a time, and validate the failed
behavior through the public API or CLI. Add a regression test when it protects
the observable contract; follow write-tests and the commit workflow for publication.
