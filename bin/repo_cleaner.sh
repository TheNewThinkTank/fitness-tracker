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

# find_large_files

# remove files from the git history
# git rm -r --cached docs/project_docs/img/
# git rm -r --cached dist/
# git rm -r --cached node_modules/
# git rm -r --cached public/build/
# git rm -r --cached .svelte-kit/
# git rm --cached .env
# git rm -r --cached .vscode/
# git rm --cached .DS_Store


# Create a New Branch
# git checkout -b cleanup

# Remove Git History
# git checkout --orphan latest_branch
# git add -A
# git commit -am "Initial commit"
# git branch -D main
# git branch -m main

# Force Push to GitHub
# git push -f origin main

# Cleanup Local Repository
# rm -rf .git/refs/original/
# git reflog expire --expire=now --all
# git gc --prune=now
# git gc --aggressive --prune=now
