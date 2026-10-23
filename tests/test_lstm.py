import pytest

pytest.importorskip("torch")


def test_lstm_forecast_shape_and_range():
    from pravaah.lstm import LSTMPredictor
    out = LSTMPredictor(steps=30).predict([.3, .32, .35, .4, .45])
    assert len(out) == 4 and all(0 <= x <= 1 for x in out)
