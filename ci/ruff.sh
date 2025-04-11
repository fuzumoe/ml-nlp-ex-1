#!/bin/bash
# should be synchronous to ruff.toml in root folder
exclude=(
    "data" \
    ".venv/"  
    )
exclude_pattern=$(printf "|^%s" "${exclude[@]}")
exclude_pattern=${exclude_pattern:1}  # Remove the leading '|'

if [ "${@: -1}" = CI ]; then
  echo "CI mode"
  changed_files=$(git diff --name-only --diff-filter=ACM HEAD~1..HEAD | grep '\.py$' | grep -v -E "$exclude_pattern")
elif [ "${IGNORE_COMMIT_HOOKS}" = true ]; then
  echo "manual override, not executing ruff"
  # manual override, for example when merging from main and mypy and linter are not same version leading to different issues for example
  exit 0  
else
  echo "git hook mode"
  changed_files=$(git diff --name-only --diff-filter=ACM HEAD | grep '\.py$' | grep -v -E "$exclude_pattern")  
fi

if [ "${@: -1}" = CI ]; then
  fmt="%s\n%s\n" 
  printf "${fmt}" "changed files:" "${changed_files}"
  printf "\nRuff: \n"
fi

if [ -n "$changed_files" ]; then
    source .venv/bin/activate
    ruff $1 $2 $changed_files 
fi