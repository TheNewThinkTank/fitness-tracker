#!/usr/bin/env bash

# show the sizes of all top-level directories
# du -sh ./* | sort -h

# sizes of all directories recursively
# du -h --max-depth=1 | sort -h

# find large files in the git history
find_large_files() {
  git rev-list --objects --all | \
  git diff-tree --stdin -r -t --no-commit-id --name-only --root | \
  sort -k2 | \
  uniq -c | \
  sort -nr
}

find_large_files

git rm -r --cached node_modules/
git rm -r --cached public/build/
git rm -r --cached .svelte-kit/
git rm --cached .env
git rm -r --cached .vscode/
git rm -r --cached .idea/
git rm --cached .DS_Store
