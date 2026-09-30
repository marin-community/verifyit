#!/bin/bash
set -euo pipefail

# Keep a runner's explicit verifyit settings; otherwise carry the old release's
# judge capability into the verifyit namespace without printing credentials.
if [ -z "${VERIFYIT_JUDGE_BASE_URL+x}" ] && [ -n "${TASKTROVE_JUDGE_BASE_URL+x}" ]; then
    export VERIFYIT_JUDGE_BASE_URL="$TASKTROVE_JUDGE_BASE_URL"
fi
if [ -z "${VERIFYIT_JUDGE_API_KEY+x}" ] && [ -n "${TASKTROVE_JUDGE_API_KEY+x}" ]; then
    export VERIFYIT_JUDGE_API_KEY="$TASKTROVE_JUDGE_API_KEY"
fi
if [ -z "${VERIFYIT_JUDGE_MODEL+x}" ] && [ -n "${TASKTROVE_JUDGE_MODEL+x}" ]; then
    export VERIFYIT_JUDGE_MODEL="$TASKTROVE_JUDGE_MODEL"
fi
if [ "$#" -eq 0 ]; then
    set -- /tests/verifier.toml
fi
exec verifyit "$@"
