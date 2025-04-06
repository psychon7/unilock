<<<<<<< HEAD
.PHONY: setup test lint run docker-up docker-down docs

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

test:
	$(PYTHON) -m pytest -v --cov=app --cov-report=html tests/

lint:
	$(PYTHON) -m black app/
	$(PYTHON) -m isort app/ 
	$(PYTHON) -m flake8 app/
	$(PYTHON) -m mypy app/

run:
	$(PYTHON) -m uvicorn app.main:app --reload

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down -v

docs:
	$(PYTHON) -m mkdocs serve

pre-commit:
	$(MAKE) lint
	$(MAKE) test
=======
test:
	pytest tests/

run:
	uvicorn app.main:app --reload
>>>>>>> db91a5192e96e6e8b41e9bb543a166b3257a9e05
