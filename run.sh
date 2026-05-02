#!/bin/bash
export PYTHONPATH=src
# Para arrancar el main: .venv/bin/python -m asimov.main
# Para arrancar el backend base con FastAPI:
.venv/bin/uvicorn asimov.api:app --host 0.0.0.0 --port 8000 --reload
