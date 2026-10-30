import pytest

from minimax_mcp.client import MinimaxAPIClient
from minimax_mcp.exceptions import MinimaxRequestError


class _Response:
    def __init__(self, status_code, status_msg, trace_id="trace-123"):
        self.headers = {"Trace-Id": trace_id}
        self._body = {"base_resp": {"status_code": status_code, "status_msg": status_msg}}

    def raise_for_status(self):
        return None

    def json(self):
        return self._body


def test_status_2061_is_a_readable_plan_error():
    client = MinimaxAPIClient("super-secret-key-xyz", "https://api.example.invalid")
    client.session.request = lambda *args, **kwargs: _Response(
        2061,
        "your current token plan not support model",
    )
    with pytest.raises(MinimaxRequestError) as caught:
        client.post("/v1/t2a_v2", json={"model": "MiniMax-Hailuo-02"})
    message = str(caught.value)
    assert "not available on your plan" in message
    assert "2061" in message
    assert "MINIMAX_DEFAULT_SPEECH_MODEL" in message
    assert "super-secret-key-xyz" not in message
    assert "trace-123" in message


def test_plan_phrase_without_2061_is_also_explained():
    client = MinimaxAPIClient("super-secret-key-xyz", "https://api.example.invalid")
    client.session.request = lambda *args, **kwargs: _Response(
        2013,
        "model not available on your plan",
        trace_id="",
    )
    with pytest.raises(MinimaxRequestError, match="not available on your plan"):
        client.post("/v1/image_generation", json={"model": "image-01"})
