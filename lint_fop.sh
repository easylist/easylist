#!/usr/bin/env bash

set -e

FOP=${TRAVIS_BUILD_DIR}/FOP.py

mkdir -p ${TRAVIS_BUILD_DIR}/output/

lint=$(python3 $FOP easylist/ easylist_adult/ easyprivacy/ fanboy-addon/)
 if grep -qiF 'Warning' $lint
 then
  printf "\n\nFOP declaire your submission contains invalid syntax.\nPlease re-check your submission\n\n"
  exit 1
 else
  printf "\n\nFOP likes your submission and believes it is valid code.\n
You should be able to merge this submission into master.\n\n"
  exit 0
 fi
