#!/usr/bin/env bash

# find large files in the git history
find_large_files() {
  git rev-list --objects --all | \
  git diff-tree --stdin -r -t --no-commit-id --name-only --root | \
  sort -k2 | \
  uniq -c | \
  sort -nr
}

find_large_files
