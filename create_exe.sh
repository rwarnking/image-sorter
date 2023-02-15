#!/bin/bash
# https://pyinstaller.org/en/v4.2/usage.html#options
PYTHONOPTIMIZE=1
pyinstaller -F --hidden-import "babel.numbers" src/application.py
for entry in "dist"/*
do
  echo "$entry"
done
