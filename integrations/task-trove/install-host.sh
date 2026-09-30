#!/bin/bash
# Copyright The Marin Authors
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
if [ "$#" -ne 1 ] || [[ ! "$1" =~ ^[0-9a-f]{40}$ ]]; then
    echo 'usage: install-host.sh <full immutable verifyit Git SHA>' >&2
    exit 2
fi
# Run at the Marin checkout root. Its committed manifest/lock are propagated
# by the normal remote launch; a host-only pip install is insufficient.
uv add "verifyit[all] @ git+https://github.com/marin-community/verifyit@$1"
