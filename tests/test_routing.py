from pravaah.routing import route
from pravaah.venue import ZONES


def calm():
    return {z: 0.2 for z in ZONES}


def test_prefers_less_congested_gate():
    p = calm(); p["Gate A"] = 0.8
    assert "Gate B" in route("Entry", "Plaza", p)["path"]


def test_blocks_gate_over_capacity():
    p = calm(); p["Gate A"] = 0.95
    r = route("Parking 1", "Zone 1", p)
    assert "Gate A" in r["avoided"] and "Gate A" not in r["path"]


def test_dst_never_blocked():
    p = calm(); p["Zone 1"] = 1.0
    assert route("Entry", "Zone 1", p)["path"][-1] == "Zone 1"
