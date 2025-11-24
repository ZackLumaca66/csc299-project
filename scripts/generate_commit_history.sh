#!/usr/bin/env bash
# Generate a compact commit history for deliverables
git --no-pager log --pretty=format:"%h %ad %an %s" --date=short --reverse "$@"
