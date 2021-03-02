#!/bin/bash
# configure virtual environment
source .venv/bin/activate && pip3 install -r requirements.txt

# run coverage tests
coverage run -m unittest discover tests && coverage report
