pyinstaller -F --hidden-import "babel.numbers" src/application.py
for entry in "dist"/*
do
  echo "$entry"
done
