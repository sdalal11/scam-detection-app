import pytest
from fastapi import HTTPException
 
import main
from models import AnalysisRequest
 
 
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
async def test_analyze_uses_context_manager_when_context_missing(monkeypatch):
    main.context_manager.clear()
    main.context_manager.add_transcript("caller asked for OTP")
 
    captured = {"context": None}
 
    async def fake_analyze_transcript(transcript, context=None):
        captured["context"] = context
        return {
            "risk_level": "medium",
            "scam_type": "phishing",
            "reasons": ["otp request"],
            "confidence": 0.8,
        }
 
    monkeypatch.setattr(main, "analyze_transcript", fake_analyze_transcript)
 
    response = await main.analyze(AnalysisRequest(transcript="please share otp"))
 
    assert response.risk_level == "medium"
    assert "caller asked for OTP" in captured["context"]
 
 
@pytest.mark.asyncio
async def test_analyze_falls_back_when_llm_returns_none(monkeypatch):
    async def fake_analyze_transcript(transcript, context=None):
        return None
 
    def fake_default_analysis():
        return {
            "risk_level": "low",
            "scam_type": None,
            "reasons": ["fallback used"],
            "confidence": 0.0,
        }
 
    monkeypatch.setattr(main, "analyze_transcript", fake_analyze_transcript)
    monkeypatch.setattr(main, "get_default_analysis", fake_default_analysis)
 
    response = await main.analyze(
        AnalysisRequest(transcript="hello", context="provided context")
    )
 
    assert response.risk_level == "low"
    assert response.reasons == ["fallback used"]
 
 
@pytest.mark.asyncio
async def test_captcha_verify_raises_on_missing_audio():
    with pytest.raises(HTTPException) as exc:
        await main.captcha_verify({})
 
    assert exc.value.status_code == 400
 
 
@pytest.mark.asyncio
async def test_captcha_verify_returns_false_when_transcription_fails(monkeypatch):
    async def fake_transcribe_audio(_audio_data):
        return None
 
    monkeypatch.setattr(main, "transcribe_audio", fake_transcribe_audio)
 
    result = await main.captcha_verify({"audio_data": "abc"})
 
    assert result["likely_human"] is False
    assert result["details"] == "Transcription failed"
 
 
@pytest.mark.asyncio
async def test_captcha_verify_parses_gemini_json_verdict(monkeypatch):
    async def fake_transcribe_audio(_audio_data):
        return "[clapping]"
 
    monkeypatch.setattr(main, "transcribe_audio", fake_transcribe_audio)
 
    content = "Verifier output: {\"likely_human\": true, \"reason\": \"clapping detected\"}"
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
 
    import httpx
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(response=response)
 
    monkeypatch.setattr(httpx, "AsyncClient", fake_client)
 
    result = await main.captcha_verify({"audio_data": "abc"})
 
    assert result["likely_human"] is True
    assert result["transcript"] == "[clapping]"
    assert result["details"] == "clapping detected"