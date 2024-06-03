.PHONY: check

check:
	isort .
	black .
	flake8 .
	bandit -r . -c "pyproject.toml"
	ruff check .
	pylint src
	mypy .

coverage-check:
	python -m coverage run -m pytest
coverage-report:
	coverage report
