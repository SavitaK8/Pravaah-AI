"""Venue graph on a 0-100 canvas. Later: load per-venue layouts from PostgreSQL/PostGIS instead."""
ZONES = {
    "Entry":     dict(xy=(8, 50),  cap=1.00, base=0.30, amp=0.10, period=90,  phase=0),
    "Gate A":    dict(xy=(38, 76), cap=0.85, base=0.25, amp=0.32, period=120, phase=0),
    "Gate B":    dict(xy=(38, 24), cap=0.85, base=0.25, amp=0.06, period=140, phase=30),
    "Plaza":     dict(xy=(64, 50), cap=0.90, base=0.30, amp=0.12, period=100, phase=10),
    "Zone 1":    dict(xy=(90, 76), cap=0.90, base=0.20, amp=0.10, period=110, phase=40),
    "Zone 2":    dict(xy=(90, 24), cap=0.90, base=0.20, amp=0.08, period=95,  phase=60),
    "Parking 1": dict(xy=(8, 12),  cap=0.95, base=0.30, amp=0.15, period=130, phase=20),
    "Parking 2": dict(xy=(8, 88),  cap=0.95, base=0.30, amp=0.20, period=105, phase=50),
}
EDGES = [("Entry", "Gate A"), ("Entry", "Gate B"), ("Gate A", "Plaza"), ("Gate B", "Plaza"),
         ("Plaza", "Zone 1"), ("Plaza", "Zone 2"), ("Parking 1", "Entry"), ("Parking 2", "Entry")]
# Fractional (x0, y0, x1, y1) box of each zone inside the camera frame (video mode only).
# CSRNet does not align cameras to maps: calibrate these per camera.
ROIS = {"Entry": (0, .4, .2, .6), "Gate A": (.2, 0, .5, .4), "Gate B": (.2, .6, .5, 1),
        "Plaza": (.5, .3, .8, .7), "Zone 1": (.8, 0, 1, .4), "Zone 2": (.8, .6, 1, 1),
        "Parking 1": (0, .8, .2, 1), "Parking 2": (0, 0, .2, .2)}
