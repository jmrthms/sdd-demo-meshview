.PHONY: setup test run seed clean
setup:            ## create the virtualenv and install
	python3 -m venv .venv && .venv/bin/pip install --quiet --upgrade pip && .venv/bin/pip install --quiet -r requirements.txt
	@echo "Done. Now: make test"
test:             ## the one command that matters
	.venv/bin/python -m pytest -q
run:              ## http://127.0.0.1:8000 — the viewer; /docs for the API
	.venv/bin/python -m uvicorn app.main:app --reload
seed:             ## regenerate data/samples/*
	.venv/bin/python scripts/make_samples.py
clean:
	rm -rf .venv .pytest_cache **/__pycache__ data/uploads meshview.db
