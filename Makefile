.PHONY: run test clean install

install:
	pip install -r requirements.txt

run:
	python run.py

test:
	python -m pytest tests/ -v

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -f todos.db
