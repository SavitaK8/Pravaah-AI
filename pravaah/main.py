import asyncio
import time
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from . import config
from .predictor import W, make_predictor
from .routing import route
from .simulator import make_source
from .venue import EDGES, ZONES

STATIC = Path(__file__).resolve().parent.parent / "static"


def level(v):
    return "high" if v >= .7 else "moderate" if v >= .45 else "low"


def slug(s):
    return s.lower().replace(" ", "-")


class Engine:
    """density source -> history -> forecast -> alerts."""

    def __init__(self):
        self.source = make_source()
        self.predictor = make_predictor(config.PREDICTOR)
        self.hist = {z: deque(maxlen=W) for z in ZONES}
        self.t, self.zones, self.alerts, self.approved = 0, {}, [], set()

    def step(self):
        self.t += 1
        for z, v in self.source.read(self.t).items():
            self.hist[z].append(v)
            fc = self.predictor.predict(self.hist[z])
            self.zones[z] = dict(xy=ZONES[z]["xy"], density=round(v, 3), forecast=[round(x, 3) for x in fc],
                                 level=level(max(v, max(fc))), ts=time.time())
        self.alerts = self._alerts()

    def forecast_peak(self):
        return {z: max(s["forecast"]) for z, s in self.zones.items()}

    def _alerts(self):
        out, peak = [], self.forecast_peak()
        for z, s in self.zones.items():
            if s["level"] == "low":
                continue
            r = route("Entry", "Plaza", peak) if z.startswith("Gate") else None
            aid = f"{slug(z)}-{s['level']}"
            out.append(dict(id=aid, zone=z, level=s["level"], approved=aid in self.approved,
                            msg=f"{z} density {'rising' if s['forecast'][-1] > s['density'] else 'high'} "
                                f"({s['density']:.2f} -> {s['forecast'][-1]:.2f})",
                            suggestion=("Reroute via " + " > ".join(r["path"])) if r and r["path"] else "Monitor / notify staff"))
        return out

    def payload(self):
        return dict(t=self.t, mode=self.source.mode, predictor=self.predictor.name, zones=self.zones, alerts=self.alerts)


@asynccontextmanager
async def lifespan(app):
    eng = app.state.engine = Engine()
    app.state.clients = set()
    eng.step()

    async def loop():
        while True:
            await asyncio.sleep(config.TICK_SECONDS)
            eng.step()
            for ws in list(app.state.clients):
                try:
                    await ws.send_json(eng.payload())
                except Exception:
                    app.state.clients.discard(ws)

    task = asyncio.create_task(loop())
    yield
    task.cancel()


app = FastAPI(title="Pravaah AI", lifespan=lifespan)


@app.get("/api/venue")
def venue():
    return dict(zones={z: p["xy"] for z, p in ZONES.items()}, edges=EDGES)


@app.get("/api/state")
def state(request: Request):
    return request.app.state.engine.payload()


@app.get("/api/route")
def get_route(request: Request, src: str, dst: str):
    if src not in ZONES or dst not in ZONES:
        raise HTTPException(404, "unknown zone")
    return route(src, dst, request.app.state.engine.forecast_peak())


@app.post("/api/alerts/{alert_id}/approve")
def approve(request: Request, alert_id: str):
    request.app.state.engine.approved.add(alert_id)  # operators approve every intervention
    return {"ok": True}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    ws.app.state.clients.add(ws)
    await ws.send_json(ws.app.state.engine.payload())
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws.app.state.clients.discard(ws)


app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
