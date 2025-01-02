#!/bin/bash
# Run linting commands
echo "Running: poetry run isort ."
poetry run isort .
if [ $? -ne 0 ]; then
    exit $?
fi

echo "Running: poetry run black ."
poetry run black .
if [ $? -ne 0 ]; then
    exit $?
fi


echo "Running: poetry run flake8 ."
poetry run flake8 .
if [ $? -ne 0 ]; then
    exit $?
fi