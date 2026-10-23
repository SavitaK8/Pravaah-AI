import os
import sys
from pathlib import Path

os.environ.setdefault("PREDICTOR", "linear")  # keep tests fast; the LSTM has its own test
os.environ.setdefault("TICK_SECONDS", "0.05")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
