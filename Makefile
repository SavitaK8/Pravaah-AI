PY ?= python3
VENV = .venv
BIN = $(VENV)/bin

.PHONY: setup setup-lite run test clean
$(VENV):
	$(PY) -m venv $(VENV)

setup: $(VENV)          ## full install (PyTorch: LSTM + CSRNet)
	$(BIN)/pip install -U pip && $(BIN)/pip install -r requirements-ml.txt -r requirements-dev.txt

setup-lite: $(VENV)     ## no PyTorch (linear-trend predictor, simulated density): small and fast
	$(BIN)/pip install -U pip && $(BIN)/pip install -r requirements-dev.txt

run:                    ## http://127.0.0.1:8000
	$(BIN)/python -m pravaah

test:
	$(BIN)/python -m pytest -q

clean:
	rm -rf $(VENV) .pytest_cache
