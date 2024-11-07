#!/bin/bash

pip install -r requirements_dev.txt

mypy .

flake8 .

DIR="images"

if [ ! -d "$DIR" ]; then
  sudo mkdir -p "$DIR"
fi

sudo chmod -R 777 images/

cd python_advanced_diploma/src

pytest -s -v ../../tests