#!/bin/bash
# Weekly brief automation — runs every Monday via cron.
# Generates this week's brief, rebuilds the static site, and logs output.

PYTHON=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
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

  echo "Done."
} >> "$LOG" 2>&1
