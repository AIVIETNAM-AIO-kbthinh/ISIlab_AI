# 🤖 AI Lab Assistant — Trợ Lý AI Phòng Thí Nghiệm

<div align="center">

**Trợ lý AI tiếng Việt dành cho phòng thí nghiệm đại học**

*Hỗ trợ hội thoại bằng giọng nói và văn bản tiếng Việt*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen3-orange.svg)](https://ollama.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

</div>

---

## 📋 Mục Lục

- [Giới Thiệu](#-giới-thiệu)
- [Tính Năng](#-tính-năng)
- [Kiến Trúc](#-kiến-trúc)
- [Yêu Cầu Hệ Thống](#-yêu-cầu-hệ-thống)
- [Cài Đặt Nhanh](#-cài-đặt-nhanh)
- [Chạy Bằng Docker](#-chạy-bằng-docker)
- [Chạy Thủ Công](#-chạy-thủ-công-không-docker)
- [Sử Dụng](#-sử-dụng)
- [API Documentation](#-api-documentation)
- [Cấu Hình](#-cấu-hình)
- [Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [Phát Triển](#-phát-triển)
- [Xử Lý Sự Cố](#-xử-lý-sự-cố)
- [Lộ Trình Phát Triển](#-lộ-trình-phát-triển)

---

## 🎯 Giới Thiệu

AI Lab Assistant là trợ lý AI hoạt động **local-first**, được thiết kế để hỗ trợ sinh viên và giảng viên trong phòng thí nghiệm đại học. Hệ thống có thể:

- **Nghe** giọng nói tiếng Việt (ASR)
- **Hiểu** và tạo câu trả lời (LLM)
- **Nói** lại bằng tiếng Việt (TTS)

Tất cả xử lý AI chạy trên server nội bộ, không gửi dữ liệu ra internet.

### Luồng Hoạt Động

```
Người dùng nói tiếng Việt
    → Hệ thống nhận dạng giọng nói (ASR)
    → LLM tạo câu trả lời
    → Hệ thống đọc lại bằng giọng Việt (TTS)
    → Người dùng nghe phản hồi
```

---

## ✨ Tính Năng

| Tính năng | Trạng thái | Mô tả |
|-----------|-----------|-------|
| 💬 Chat văn bản | ✅ Phase 1 | Hỏi đáp bằng tiếng Việt |
| 🎤 Chat giọng nói | ✅ Phase 1 | Nói tiếng Việt, nhận phản hồi bằng giọng |
| 🔊 Text-to-Speech | ✅ Phase 1 | Giọng Việt tự nhiên (edge-tts) |
| 🎙️ Speech-to-Text | ✅ Phase 1 | Nhận dạng giọng Việt (faster-whisper) |
| 🧠 LLM Local | ✅ Phase 1 | Ollama + Qwen3 chạy local |
| 🌐 Web UI | ✅ Phase 1 | Giao diện web responsive, dark mode |
| 📚 RAG Documents | 🔜 Phase 2 | Trả lời từ tài liệu phòng lab |
| 👥 Multi-client | 🔜 Phase 3 | Nhiều thiết bị cùng sử dụng |

---

## 🏗️ Kiến Trúc

```
┌──────────────────────────────────────────────────┐
│                  Web Browser / Client             │
│         (Microphone + Speaker + UI)               │
└────────────────────┬─────────────────────────────┘
                     │ HTTP / WebSocket
┌────────────────────┴─────────────────────────────┐
│              API Gateway (:8000)                   │
│     FastAPI + WebSocket + Static Files             │
└──┬──────────────┬──────────────┬─────────────────┘
   │              │              │
┌──┴───┐    ┌─────┴────┐   ┌────┴───┐
│ ASR  │    │   LLM    │   │  TTS   │
│:8001 │    │  :8003   │   │ :8002  │
│      │    │          │   │        │
│faster│    │  Ollama  │   │edge-tts│
│whisper│   │ Qwen3 8B │   │        │
└──────┘    └──────────┘   └────────┘
```

Chi tiết: [docs/architecture.md](docs/architecture.md)

---

## 💻 Yêu Cầu Hệ Thống

### Tối thiểu (Development)

| Thành phần | Yêu cầu |
|-----------|---------|
| OS | Windows 10/11, Ubuntu 20.04+, macOS |
| Python | 3.11+ |
| RAM | 16 GB |
| CPU | 6-8 cores |
| GPU | Không bắt buộc (chạy CPU) |
| Dung lượng | 20-50 GB |

### Phần mềm cần cài đặt

1. **Python 3.11+** — [python.org](https://www.python.org/downloads/)
2. **Ollama** — [ollama.com](https://ollama.com/download)
3. **FFmpeg** — [ffmpeg.org](https://ffmpeg.org/download.html)
4. **Docker & Docker Compose** (tùy chọn) — [docker.com](https://docs.docker.com/get-docker/)

---

## 🚀 Cài Đặt Nhanh

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd ISIlab_AI
```

### Bước 2: Cài Ollama và tải model

```bash
# Đảm bảo Ollama đang chạy
ollama serve

# Tải model (chọn 1 trong các lựa chọn)
ollama pull qwen3:8b      # Khuyến nghị (cần ~8GB RAM)
# ollama pull qwen3:4b    # Máy yếu hơn (~4GB RAM)
# ollama pull qwen3:14b   # GPU mạnh (~16GB VRAM)
```

### Bước 3: Tạo file cấu hình

```bash
cp .env.example .env
```

Chỉnh sửa `.env` nếu cần (ví dụ: đổi model, port, voice).

---

## 🐳 Chạy Bằng Docker

> **Yêu cầu:** Docker, Docker Compose, và Ollama đang chạy trên host.

```bash
# Build và khởi chạy tất cả services
docker compose up --build

# Chạy nền (background)
docker compose up --build -d

# Xem logs
docker compose logs -f

# Dừng
docker compose down
```

Mở browser: **http://localhost:8000**

---

## 🔧 Chạy Thủ Công (Không Docker)

### Bước 1: Cài dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt
venv\Scripts\activate        # Windows (CMD)
venv\Scripts\Activate.ps1    # Windows (PowerShell)
# source venv/bin/activate   # Linux/macOS

# Cài đặt packages
pip install -r requirements.txt
```

### Bước 2: Đảm bảo Ollama đang chạy

```bash
ollama serve
```

### Bước 3: Chạy từng service

Mở **4 terminal** riêng biệt, mỗi terminal chạy 1 service:

**Terminal 1 — ASR Service (Speech-to-Text):**
```bash
cd services/asr_service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 — LLM Service (Language Model):**
```bash
cd services/llm_service
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Terminal 3 — TTS Service (Text-to-Speech):**
```bash
cd services/tts_service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 4 — API Gateway (Main Entry Point):**
```bash
cd services/api_gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Bước 4: Mở browser

Truy cập: **http://localhost:8000**

---

## 📖 Sử Dụng

### Chat Văn Bản
1. Mở **http://localhost:8000**
2. Nhập tin nhắn tiếng Việt vào ô chat
3. Nhấn **Enter** hoặc nút **Gửi**
4. Chờ phản hồi từ trợ lý

### Chat Giọng Nói
1. Nhấn nút **🎤 Micro** để bắt đầu ghi âm
2. Nói tiếng Việt
3. Nhấn lại nút micro để dừng
4. Hệ thống sẽ:
   - Hiển thị bản phiên âm (transcript)
   - Hiển thị câu trả lời
   - Tự động phát lại bằng giọng nói

### Ví Dụ Câu Hỏi

```
Xin chào, bạn là ai?
Bạn có thể làm gì?
Nội quy phòng lab là gì?
Làm sao để sử dụng máy in 3D trong phòng lab?
```

---

## 📡 API Documentation

### Endpoints chính

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/health` | Kiểm tra trạng thái services |
| `GET` | `/models` | Liệt kê models LLM có sẵn |
| `POST` | `/chat/text` | Chat văn bản |
| `POST` | `/chat/voice` | Chat giọng nói (upload audio) |
| `WS` | `/ws/voice` | WebSocket real-time voice |
| `POST` | `/asr/transcribe` | Nhận dạng giọng nói |
| `POST` | `/tts/synthesize` | Tổng hợp giọng nói |

### Test nhanh với curl

```bash
# Kiểm tra health
curl http://localhost:8000/health

# Chat văn bản
curl -X POST http://localhost:8000/chat/text \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào, bạn là ai?"}'

# Xem models
curl http://localhost:8000/models
```

Chi tiết API: [docs/api.md](docs/api.md)

---

## ⚙️ Cấu Hình

### Biến môi trường chính (`.env`)

| Biến | Mặc định | Mô tả |
|------|---------|-------|
| `OLLAMA_MODEL` | `qwen3:8b` | Model LLM sử dụng |
| `ASR_MODEL_SIZE` | `base` | Kích thước model ASR: tiny, base, small, medium, large |
| `ASR_DEVICE` | `cpu` | Device cho ASR: cpu hoặc cuda |
| `TTS_VOICE` | `vi-VN-HoaiMyNeural` | Giọng TTS tiếng Việt |
| `TTS_ENGINE` | `edge-tts` | Engine TTS: edge-tts, piper, vixtts |
| `LOG_LEVEL` | `INFO` | Mức log: DEBUG, INFO, WARNING, ERROR |

### Giọng nói TTS có sẵn

| Voice | Giới tính | Ghi chú |
|-------|----------|---------|
| `vi-VN-HoaiMyNeural` | Nữ | Mặc định, giọng tự nhiên |
| `vi-VN-NamMinhNeural` | Nam | Giọng nam |

---

## 📁 Cấu Trúc Dự Án

```
ISIlab_AI/
├── README.md                 # Hướng dẫn này
├── plan.md                   # Kế hoạch phát triển chi tiết
├── docker-compose.yml        # Docker Compose config
├── .env.example              # Template biến môi trường
├── requirements.txt          # Dependencies (chạy local)
│
├── services/                 # Backend microservices
│   ├── api_gateway/          # API Gateway (FastAPI)
│   │   ├── main.py           # Entry point
│   │   ├── core/             # Config & service clients
│   │   ├── routes/           # API endpoints
│   │   └── schemas/          # Pydantic models
│   │
│   ├── asr_service/          # Speech-to-Text
│   │   ├── main.py           # FastAPI app
│   │   ├── transcriber.py    # Whisper wrapper
│   │   └── audio_preprocess.py
│   │
│   ├── llm_service/          # LLM (Ollama wrapper)
│   │   ├── main.py           # FastAPI app
│   │   ├── ollama_client.py  # Ollama HTTP client
│   │   └── prompts.py        # System prompts (Vietnamese)
│   │
│   └── tts_service/          # Text-to-Speech
│       ├── main.py           # FastAPI app
│       ├── synthesizer.py    # edge-tts wrapper
│       └── text_normalizer.py# Vietnamese text normalization
│
├── frontend/web/             # Web frontend
│   ├── index.html            # Main HTML
│   ├── style.css             # Styles (dark theme)
│   └── app.js                # Client-side JavaScript
│
├── configs/                  # Configuration files
│   ├── dev.yaml              # Development config
│   └── prompts.yaml          # LLM system prompts
│
├── data/                     # Data files
│   ├── documents/            # Lab documents (Phase 2 RAG)
│   ├── audio_samples/        # Test audio files
│   └── logs/                 # Application logs
│
├── models/                   # AI model files
│   ├── asr/                  # ASR models
│   ├── tts/                  # TTS voices
│   └── embedding/            # Embedding models (Phase 2)
│
├── tests/                    # Test suite
│   ├── conftest.py           # Test fixtures
│   ├── test_asr.py           # ASR tests
│   ├── test_llm.py           # LLM tests
│   ├── test_tts.py           # TTS tests
│   └── test_e2e_voice.py     # End-to-end tests
│
└── docs/                     # Documentation
    ├── architecture.md       # Kiến trúc hệ thống
    ├── api.md                # API documentation
    └── deployment.md         # Hướng dẫn triển khai
```

---

## 🧪 Phát Triển

### Chạy tests

```bash
# Đảm bảo tất cả services đang chạy, sau đó:
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### Swagger UI

Khi API Gateway đang chạy, truy cập:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Đổi model LLM

```bash
# Tải model mới
ollama pull qwen3:4b

# Cập nhật .env
OLLAMA_MODEL=qwen3:4b

# Restart LLM service
```

### Đổi giọng TTS

Cập nhật trong `.env`:
```bash
TTS_VOICE=vi-VN-NamMinhNeural  # Giọng nam
```

---

## 🔧 Xử Lý Sự Cố

### Ollama không kết nối được

```bash
# Kiểm tra Ollama đang chạy
ollama list

# Nếu chưa chạy
ollama serve

# Test trực tiếp
curl http://localhost:11434/
```

### ASR Service không load model

```bash
# Kiểm tra log
docker compose logs asr-service

# Thử model nhỏ hơn
ASR_MODEL_SIZE=tiny  # trong .env
```

### Không có âm thanh từ TTS

- Kiểm tra kết nối internet (edge-tts cần internet)
- Kiểm tra browser cho phép autoplay
- Thử phát lại bằng nút "Phát lại" trong tin nhắn

### Docker: lỗi "host.docker.internal"

Trên Linux, thêm vào docker-compose.yml:
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

### Port bị chiếm

```bash
# Windows
netstat -ano | findstr :8000

# Linux
lsof -i :8000
```

---

## 🗺️ Lộ Trình Phát Triển

| Phase | Mục tiêu | Trạng thái |
|-------|---------|-----------|
| **Phase 1** | Voice Chat MVP | ✅ Hoàn thành |
| **Phase 2** | Lab Knowledge Assistant (RAG) | 🔜 Tiếp theo |
| **Phase 3** | Multi-Client Lab Deployment | 📋 Kế hoạch |
| **Phase 4** | Production Hardening | 📋 Kế hoạch |

Chi tiết: [plan.md](plan.md)

---

## 📄 License

MIT License

---

<div align="center">
<sub>Built with ❤️ for ISI Lab</sub>
</div>