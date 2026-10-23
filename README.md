# Pravaah AI (hackathon prototype)

AI-assisted crowd and traffic management: density heatmaps -> LSTM forecast -> congestion-aware routing -> operator-approved alerts.

```
pravaah/            backend package (FastAPI)
  main.py             API + WebSocket + engine loop (source -> forecast -> alerts)
  simulator.py        simulated density (default) or CSRNet-on-video source
  csrnet.py           CSRNet model + frame -> density map
  lstm.py / predictor.py   LSTM forecaster (+ linear fallback when PyTorch is absent)
  routing.py          Dijkstra with forecast-weighted costs, capacity blocking
  venue.py            zone graph + camera ROIs (calibrate per camera)
static/index.html   React + Leaflet dashboard (served by FastAPI)
tests/              pytest
```

## Run (macOS / Linux)
```bash
make setup-lite     # quick, no PyTorch: simulated density + linear predictor
# or: make setup    # full: PyTorch LSTM + CSRNet (large download)
make run            # http://127.0.0.1:8000
make test
```

## Run (Windows PowerShell)
```powershell
python -m venv .venv; .venv\Scripts\activate
pip install -r requirements-ml.txt -r requirements-dev.txt   # or only requirements-dev.txt for lite
python -m pravaah
```

## Real detection
```bash
VIDEO_PATH=data/crowd.mp4 CSRNET_WEIGHTS=data/csrnet.pth make run
```
Needs CSRNet weights trained on ShanghaiTech/UCF-QNRF. Tune `ROIS` in `venue.py` and `PEOPLE_AT_FULL` (env) for your camera.
Settings: see `.env.example`.

## API
`GET /api/venue` · `GET /api/state` · `GET /api/route?src=&dst=` · `POST /api/alerts/{id}/approve` · `WS /ws`

## Not built yet
PostGIS persistence, attendee QR page, venue-upload UI, reroute outcome checks, stale-feed warnings.
