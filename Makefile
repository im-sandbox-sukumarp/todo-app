# Copyright (c) InfoMCopilot-KR. All rights reserved.

.PHONY: run test coverage clean install install-dev

PYTHON ?= python

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	$(PYTHON) run.py

test:
	$(PYTHON) -m unittest discover -v

coverage:
	$(PYTHON) -m coverage run --source=todoapp -m unittest discover
	$(PYTHON) -m coverage report -m

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -f todos.db
	rm -f .coverage
