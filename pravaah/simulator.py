"""Density sources: a simulator (default) or CSRNet on a video file (needs weights)."""
import math
import random

from . import config
from .venue import ROIS, ZONES


class SimSource:
    mode = "simulated"

    def read(self, t):
        out = {}
        for z, p in ZONES.items():
            v = p["base"] + p["amp"] * (1 - math.cos(2 * math.pi * (t + p["phase"]) / p["period"]))
            out[z] = min(1.0, max(0.0, v + random.gauss(0, 0.01)))
        return out


class VideoSource:
    mode = "csrnet-video"

    def __init__(self):
        import cv2
        import torch
        from . import csrnet
        self.cv2, self.csr = cv2, csrnet
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = csrnet.load(config.CSRNET_WEIGHTS, self.device)
        self.cap = cv2.VideoCapture(config.VIDEO_PATH)
        if not self.cap.isOpened():
            raise RuntimeError(f"cannot open video: {config.VIDEO_PATH}")

    def read(self, t):
        ok, frame = self.cap.read()
        if not ok:  # loop the clip
            self.cap.set(self.cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = self.cap.read()
        d = self.csr.density(self.model, frame, self.device)
        h, w = d.shape
        return {z: min(1.0, float(d[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)].sum()) / config.PEOPLE_AT_FULL)
                for z, (x0, y0, x1, y1) in ROIS.items()}


def make_source():
    return VideoSource() if config.VIDEO_PATH and config.CSRNET_WEIGHTS else SimSource()
