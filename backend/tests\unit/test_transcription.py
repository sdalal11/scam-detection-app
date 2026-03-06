import base64
 
import pytest
 
from services import transcription
 
 
class FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text
 
    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload or {}
 
 
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
 
 
def long_audio_base64() -> str:
    return base64.b64encode(b"a" * 400).decode("utf-8")
 
 
@pytest.mark.asyncio
async def test_transcribe_audio_success(monkeypatch):
    monkeypatch.setattr(transcription, "ELEVENLABS_API_KEY", "xi_test_key")
    response = FakeResponse(200, {"text": "hello from call"})
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(response=response)
 
    monkeypatch.setattr(transcription.httpx, "AsyncClient", fake_client)
 
    result = await transcription.transcribe_audio(long_audio_base64())
 
    assert result == "hello from call"
 
 
@pytest.mark.asyncio
async def test_transcribe_audio_network_failure_returns_none(monkeypatch):
    monkeypatch.setattr(transcription, "ELEVENLABS_API_KEY", "xi_test_key")
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(exc=RuntimeError("timeout"))
 
    monkeypatch.setattr(transcription.httpx, "AsyncClient", fake_client)
 
    result = await transcription.transcribe_audio(long_audio_base64())
 
    assert result is None
 
 
@pytest.mark.asyncio
async def test_transcribe_audio_non_200_returns_none(monkeypatch):
    monkeypatch.setattr(transcription, "ELEVENLABS_API_KEY", "xi_test_key")
    response = FakeResponse(500, {"error": "server"}, text="server error")
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(response=response)
 
    monkeypatch.setattr(transcription.httpx, "AsyncClient", fake_client)
 
    result = await transcription.transcribe_audio(long_audio_base64())
 
    assert result is None
 
 
@pytest.mark.asyncio
async def test_transcribe_audio_malformed_json_returns_none(monkeypatch):
    monkeypatch.setattr(transcription, "ELEVENLABS_API_KEY", "xi_test_key")
    response = FakeResponse(200, ValueError("bad json"))
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(response=response)
 
    monkeypatch.setattr(transcription.httpx, "AsyncClient", fake_client)
 
    result = await transcription.transcribe_audio(long_audio_base64())
 
    assert result is None
 
 
@pytest.mark.asyncio
async def test_transcribe_audio_empty_input_returns_empty_string(monkeypatch):
    monkeypatch.setattr(transcription, "ELEVENLABS_API_KEY", "xi_test_key")
 
    result = await transcription.transcribe_audio("")
 
    assert result == ""
 
 
@pytest.mark.asyncio
async def test_transcribe_audio_auth_401_returns_none(monkeypatch):
    monkeypatch.setattr(transcription, "ELEVENLABS_API_KEY", "xi_test_key")
    response = FakeResponse(401, {"detail": "Unauthorized"}, text="Unauthorized")
 
    def fake_client(*args, **kwargs):
        return FakeAsyncClient(response=response)
 
    monkeypatch.setattr(transcription.httpx, "AsyncClient", fake_client)
 
    result = await transcription.transcribe_audio(long_audio_base64())
 
    assert result is None
 
 
@pytest.mark.asyncio
async def test_validate_audio_format_with_valid_base64_returns_true():
    valid_audio = base64.b64encode(b"sample-audio-bytes").decode("utf-8")
 
    result = await transcription.validate_audio_format(valid_audio)
 
    assert result is True
 
 
@pytest.mark.asyncio
async def test_validate_audio_format_with_invalid_base64_returns_false():
    result = await transcription.validate_audio_format("not-base64-@@@")
 
    assert result is False