import heapq
import math

from .venue import EDGES, ZONES


def _graph():
    g = {z: [] for z in ZONES}
    for a, b in EDGES:
        d = math.dist(ZONES[a]["xy"], ZONES[b]["xy"])
        g[a].append((b, d))
        g[b].append((a, d))
    return g


GRAPH = _graph()


def route(src, dst, pred):
    """Dijkstra. Edge cost = length * (1 + 4 * predicted density of the next zone).
    Zones predicted at/over capacity are skipped (except src/dst). `pred` maps zone -> density."""
    blocked = {z for z in ZONES if pred[z] >= ZONES[z]["cap"]} - {src, dst}
    pq, seen = [(0.0, src, [src])], set()
    while pq:
        cost, node, path = heapq.heappop(pq)
        if node == dst:
            return {"path": path, "cost": round(cost, 1), "avoided": sorted(blocked)}
        if node in seen:
            continue
        seen.add(node)
        for nxt, d in GRAPH[node]:
            if nxt not in blocked and nxt not in seen:
                heapq.heappush(pq, (cost + d * (1 + 4 * pred[nxt]), nxt, path + [nxt]))
    return {"path": [], "cost": None, "avoided": sorted(blocked)}
