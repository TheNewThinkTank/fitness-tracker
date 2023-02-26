#!/usr/local/bin/bash

# prerequisites:
# all tags deleted
# main branch is the only branch that exists

# purpose: remove all git history

: '
git checkout --orphan last
git add -A
git commit -am "feat: rewrite git history" --no-verify
git branch -D main
git branch -m main
git push -f origin main
git gc --aggressive --prune=all
'
