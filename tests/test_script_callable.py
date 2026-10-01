# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0

import time

import pytest

from verifyit.grade import InvalidTask, Reward, Status, scored
from verifyit.modes.grade_script import grade_script_callable


def trusted_script(behavior):
    if behavior == "invalid_reference":
        raise InvalidTask("missing trusted reference")
    if behavior == "runtime_failure":
        raise RuntimeError("scorer dependency unavailable")
    if behavior == "timeout":
        time.sleep(10)
    if behavior == "unscored_positive":
        return Reward(1, Status.INFRA_ERROR)
    if behavior == "nonfinite":
        return Reward(float("nan"), Status.SCORED)
    if behavior == "malformed":
        return {"reward": 1, "status": "scored"}
    if behavior == "invalid_detail":
        return Reward(1, Status.SCORED, {"value": float("inf")})
    print("ordinary grader output")
    return scored(0.25, observations=[True, False, False, False])


@pytest.mark.parametrize(
    "behavior,status,reward",
    [
        ("success", Status.SCORED, 0.25),
        ("invalid_reference", Status.INVALID_TASK, 0),
        ("runtime_failure", Status.INFRA_ERROR, 0),
        ("unscored_positive", Status.INFRA_ERROR, 0),
        ("nonfinite", Status.INFRA_ERROR, 0),
        ("malformed", Status.INFRA_ERROR, 0),
        ("invalid_detail", Status.INFRA_ERROR, 0),
        ("timeout", Status.INFRA_ERROR, 0),
    ],
)
def test_script_callable_preserves_status_and_rejects_unusable_rewards(behavior, status, reward):
    verdict = grade_script_callable(trusted_script, behavior, timeout=0.3 if behavior == "timeout" else 5)
    assert (verdict.status, verdict.reward) == (status, reward)
    if behavior == "success":
        assert verdict.detail == {"observations": [True, False, False, False]}
