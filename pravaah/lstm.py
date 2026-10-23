"""LSTM near-future density forecaster. Trains on synthetic series at startup (a few seconds on CPU);
swap `synth` for logged zone-density sequences from real footage."""
import numpy as np
import torch
import torch.nn as nn

from .predictor import H, W


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(1, 32, batch_first=True)
        self.out = nn.Linear(32, H)

    def forward(self, x):
        y, _ = self.lstm(x)
        return torch.sigmoid(self.out(y[:, -1]))


def synth(n):
    t = np.arange(W + H)[None] + np.random.rand(n, 1) * 150
    p = np.random.uniform(80, 160, (n, 1))
    b = np.random.uniform(.2, .45, (n, 1))
    a = np.random.uniform(.03, .3, (n, 1))
    return np.clip(b + a * (1 - np.cos(2 * np.pi * t / p)) + np.random.randn(n, W + H) * .01, 0, 1).astype("float32")


class LSTMPredictor:
    name = "lstm"

    def __init__(self, steps=250):
        torch.manual_seed(0)
        np.random.seed(0)
        self.net = Net()
        opt = torch.optim.Adam(self.net.parameters(), 1e-2)
        for _ in range(steps):
            d = torch.from_numpy(synth(128))
            loss = nn.functional.mse_loss(self.net(d[:, :W, None]), d[:, W:])
            opt.zero_grad()
            loss.backward()
            opt.step()
        self.net.eval()
        self.train_loss = float(loss)

    @torch.no_grad()
    def predict(self, hist):
        h = list(hist)[-W:]
        h = [h[0]] * (W - len(h)) + h
        return self.net(torch.tensor(h, dtype=torch.float32)[None, :, None])[0].tolist()
