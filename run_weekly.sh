#!/bin/bash
# Weekly brief automation — runs every Monday via cron.
# Generates this week's brief, rebuilds the static site, commits, and pushes.

PYTHON=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
GIT=/usr/bin/git
DIR=/Users/grayj/Desktop/GroundZero/project1-weekly-brief
LOG=$DIR/run_weekly.log

{
  echo "===== $(date) ====="
  cd "$DIR" || exit 1

  echo "Generating brief..."
  $PYTHON research-project-weekly-brief.py
  if [ $? -ne 0 ]; then
    echo "ERROR: brief generation failed."
    exit 1
  fi

  echo "Building site..."
  $PYTHON build.py --no-open
  if [ $? -ne 0 ]; then
    echo "ERROR: site build failed."
    exit 1
  fi

  echo "Committing and pushing to GitHub..."
  $GIT add brief-*.md index.html
  $GIT commit -m "Weekly brief — $(date +%Y-%m-%d)"
  if [ $? -ne 0 ]; then
    echo "NOTE: Nothing new to commit (brief may already exist)."
  else
    $GIT push origin main
    if [ $? -ne 0 ]; then
      echo "WARNING: git push failed. Brief saved locally but not pushed."
    else
      echo "Pushed to GitHub."
    fi
  fi

  echo "Done."
} >> "$LOG" 2>&1
