# Kiến Trúc Hệ Thống — AI Lab Assistant

## Tổng Quan

AI Lab Assistant sử dụng kiến trúc **microservices**, với mỗi thành phần AI chạy độc lập và giao tiếp qua HTTP REST API.

## Sơ Đồ Kiến Trúc

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Web      │  │ Kiosk PC │  │ Rasp. Pi │  │ Mobile   │    │
│  │ Browser  │  │          │  │          │  │ Browser  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └──────────────┴──────────────┴──────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP / WebSocket
┌───────────────────────────┴─────────────────────────────────┐
│                   API Gateway (:8000)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ /chat/text  │ │ /chat/voice │ │ /ws/voice   │            │
│  │ /asr/*      │ │ /tts/*      │ │ /health     │            │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘            │
└─────────┼───────────────┼───────────────┼───────────────────┘
          │               │               │
   ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐
   │ ASR Service │ │ LLM Service │ │ TTS Service │
   │   (:8001)   │ │   (:8003)   │ │   (:8002)   │
   │             │ │             │ │             │
   │ faster-     │ │ Ollama      │ │ edge-tts    │
   │ whisper     │ │ Qwen3 8B   │ │             │
   └─────────────┘ └──────┬──────┘ └─────────────┘
                          │
                   ┌──────┴──────┐
                   │   Ollama    │
                   │  (:11434)   │
                   │  (on host)  │
                   └─────────────┘
```

## Luồng Xử Lý

### Text Chat
```
User → API Gateway → LLM Service → Ollama → Response
```

### Voice Chat
```
User → Microphone → API Gateway → ASR Service → Transcript
                                      ↓
                                 LLM Service → Response text
                                      ↓
                                 TTS Service → Audio
                                      ↓
                                 API Gateway → User (audio + text)
```

## Cổng Mạng (Ports)

| Service      | Port  | Mô tả                    |
|-------------|-------|--------------------------|
| API Gateway | 8000  | Entry point chính        |
| ASR Service | 8001  | Speech-to-Text           |
| TTS Service | 8002  | Text-to-Speech           |
| LLM Service | 8003  | LLM wrapper              |
| Ollama      | 11434 | LLM engine (trên host)   |
| Qdrant      | 6333  | Vector DB (Phase 2)      |

## Giao Tiếp Giữa Services

Tất cả services giao tiếp qua **HTTP REST API** (JSON). API Gateway là entry point duy nhất cho clients.
