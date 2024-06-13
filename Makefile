.PHONY: check

check: lint test

lint:
	isort .
	black .
	flake8 .
	bandit -r . -c "pyproject.toml"
	ruff check .
	pylint src
	mypy .

test:
	pytest tests -v

cov:
	python -m coverage run -m pytest

covrep:
	coverage report
