.PHONY: check

check:
	isort .
	black .
	flake8 .
	bandit -r .
	ruff check .
	pylint src
	mypy .
