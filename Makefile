PYTHON ?= python3.11
PIP ?= $(PYTHON) -m pip
SERVICE ?= ba_agent
APP_MODULE = services.$(SERVICE).app.main:app

.PHONY: setup lint test run-local

setup:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt

lint:
	ruff check .
	black --check .
	mypy .

test:
	pytest

run-local:
	uvicorn $(APP_MODULE) --reload --host 0.0.0.0 --port 8000
