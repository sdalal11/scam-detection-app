import pytest
 
from services import llm_analysis
 
 
class FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text
 
    def json(self):
        return self._payload
 
 
class FakeAsyncClient:
    def __init__(self, response=None, exc=None, *args, **kwargs):
        self._response = response
        self._exc = exc
 
    async def __aenter__(self):
        return self
 
    async def __aexit__(self, exc_type, exc, tb):
        return False
 
    async def post(self, *args, **kwargs):
        if self._exc:
            raise self._exc
        return self._response
 
 
@pytest.mark.asyncio
async def test_analyze_transcript_normalizes_risk_level(monkeypatch):
    monkeypatch.setattr(llm_analysis, "GEMINI_API_KEY", "test-key")
 
    content = """
    Here is the result:
    ```json
    {"risk_level":"HIGH","scam_type":"bank scam","reasons":["urgency"],"confidence":"0.92"}
    ```
    """
 
    response = FakeResponse(
        200,
        {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": content}]
                    }
                }
            ]
        },
    )
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(response=response)
 
    monkeypatch.setattr(llm_analysis.httpx, "AsyncClient", fake_client)
 
    analysis = await llm_analysis.analyze_transcript("verify your account", "prior context")
 
    assert analysis["risk_level"] == "high"
    assert analysis["scam_type"] == "bank scam"
    assert analysis["reasons"] == ["urgency"]
    assert analysis["confidence"] == pytest.approx(0.92)
 
 
@pytest.mark.asyncio
async def test_analyze_transcript_returns_default_on_http_error(monkeypatch):
    monkeypatch.setattr(llm_analysis, "GEMINI_API_KEY", "test-key")
 
    response = FakeResponse(500, text="Internal error")
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(response=response)
 
    monkeypatch.setattr(llm_analysis.httpx, "AsyncClient", fake_client)
 
    analysis = await llm_analysis.analyze_transcript("suspicious content")
 
    assert analysis == llm_analysis.get_default_analysis()
 
 
@pytest.mark.asyncio
async def test_analyze_transcript_returns_default_on_exception(monkeypatch):
    monkeypatch.setattr(llm_analysis, "GEMINI_API_KEY", "test-key")
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(exc=RuntimeError("network down"))
 
    monkeypatch.setattr(llm_analysis.httpx, "AsyncClient", fake_client)
 
    analysis = await llm_analysis.analyze_transcript("suspicious content")
 
    assert analysis == llm_analysis.get_default_analysis()