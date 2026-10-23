"""Forecasters: LSTM when PyTorch is installed, otherwise a linear-trend fallback so the app still runs."""
W, H = 8, 4  # history window, forecast horizon (ticks)


class LinearPredictor:
    name = "linear-trend"

    def predict(self, hist):
        h = list(hist)[-4:]
        slope = (h[-1] - h[0]) / max(1, len(h) - 1)
        return [min(1.0, max(0.0, h[-1] + slope * (i + 1))) for i in range(H)]


def make_predictor(kind="auto"):
    if kind != "linear":
        try:
            from .lstm import LSTMPredictor
            return LSTMPredictor()
        except ImportError:
            if kind == "lstm":
                raise
            print("PyTorch not installed -> using linear-trend predictor (make setup for the LSTM)")
    return LinearPredictor()
