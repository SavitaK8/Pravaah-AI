"""All runtime settings come from environment variables (see .env.example)."""
import os

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
TICK_SECONDS = float(os.getenv("TICK_SECONDS", "2"))
PREDICTOR = os.getenv("PREDICTOR", "auto")        # auto | lstm | linear
VIDEO_PATH = os.getenv("VIDEO_PATH")              # set together with CSRNET_WEIGHTS for real detection
CSRNET_WEIGHTS = os.getenv("CSRNET_WEIGHTS")
PEOPLE_AT_FULL = float(os.getenv("PEOPLE_AT_FULL", "40"))  # people in a zone ROI that count as density 1.0
