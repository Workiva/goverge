#!/usr/bin/env bash
TRACKING_REMOTE="$(git for-each-ref --format='%(upstream:short)' $(git symbolic-ref -q HEAD) | cut -d'/' -f1 | xargs git ls-remote --get-url | cut -d':' -f2 | sed 's/.git$//')"
codecov -u https://codecov.io -r $TRACKING_REMOTE --no-fail