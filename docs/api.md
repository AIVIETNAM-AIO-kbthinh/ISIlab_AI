# API Documentation — AI Lab Assistant

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### Health Check

#### `GET /health`

Kiểm tra trạng thái tất cả services.

**Response:**
```json
{
    "status": "healthy",
    "services": {
        "asr": {"status": "healthy", "detail": {...}},
        "llm": {"status": "healthy", "detail": {...}},
        "tts": {"status": "healthy", "detail": {...}}
    },
    "version": "0.1.0"
}
```

#### `GET /models`

Liệt kê các model LLM có sẵn trong Ollama.

**Response:**
```json
{
    "models": [
        {"name": "qwen3:8b", "size": "4.9 GB"}
    ]
}
```

---

### Text Chat

#### `POST /chat/text`

Chat bằng văn bản.

**Request Body:**
```json
{
    "message": "Xin chào, bạn là ai?",
    "conversation_id": "optional_conv_id",
    "model": "qwen3:8b"
}
```

**Response:**
```json
{
    "reply": "Xin chào! Tôi là Lab Assistant...",
    "model": "qwen3:8b",
    "latency_ms": 1234.5
}
```

---

### Voice Chat

#### `POST /chat/voice`

Chat bằng giọng nói. Gửi file audio, nhận lại text + audio response.

**Request:** `multipart/form-data`
- `audio`: File audio (wav, webm, ogg, mp3)

**Response:**
```json
{
    "transcript": "Xin chào, bạn là ai?",
    "reply": "Xin chào! Tôi là Lab Assistant...",
    "audio_url": "base64_encoded_audio...",
    "model": "qwen3:8b",
    "latency": {
        "asr_ms": 500,
        "llm_ms": 2000,
        "tts_ms": 800,
        "total_ms": 3300
    }
}
```

#### `WebSocket /ws/voice`

Real-time voice streaming.

**Client → Server:** Binary audio data

**Server → Client:** JSON messages:
```json
{"type": "transcript", "text": "...", "asr_ms": 500}
{"type": "reply", "text": "...", "llm_ms": 2000}
{"type": "audio", "audio_base64": "...", "latency": {...}}
```

---

### ASR (Speech-to-Text)

#### `POST /asr/transcribe`

Chuyển đổi audio thành văn bản.

**Request:** `multipart/form-data`
- `audio`: File audio

**Response:**
```json
{
    "text": "Nội quy phòng lab là gì?",
    "language": "vi",
    "confidence": 0.87,
    "duration_ms": 1320
}
```

---

### TTS (Text-to-Speech)

#### `POST /tts/synthesize`

Chuyển đổi văn bản thành giọng nói.

**Request Body:**
```json
{
    "text": "Xin chào, tôi là trợ lý phòng thí nghiệm.",
    "voice": "vi-VN-HoaiMyNeural"
}
```

**Response:**
```json
{
    "audio_base64": "base64_encoded_mp3...",
    "duration_ms": 2400
}
```
