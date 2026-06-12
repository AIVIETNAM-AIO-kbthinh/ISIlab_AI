# Hướng Dẫn Triển Khai — AI Lab Assistant

## 1. Triển Khai Development (Local)

### Yêu cầu
- Python 3.11+
- Ollama đã cài đặt và chạy
- FFmpeg (cho xử lý audio)
- Docker & Docker Compose (tùy chọn)

### Cách 1: Chạy trực tiếp (không Docker)

```bash
# 1. Clone repository
git clone <repo-url>
cd ISIlab_AI

# 2. Tạo file .env
cp .env.example .env
# Chỉnh sửa .env nếu cần

# 3. Cài Ollama model
ollama pull qwen3:8b

# 4. Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 5. Cài dependencies
pip install -r requirements.txt

# 6. Chạy từng service (mỗi service trong 1 terminal riêng)

# Terminal 1: ASR Service
cd services/asr_service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: LLM Service
cd services/llm_service
uvicorn main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 3: TTS Service
cd services/tts_service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 4: API Gateway
cd services/api_gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Cách 2: Docker Compose

```bash
# 1. Tạo file .env
cp .env.example .env

# 2. Đảm bảo Ollama đang chạy trên host
ollama serve

# 3. Build và chạy
docker compose up --build

# 4. Mở browser
# http://localhost:8000
```

## 2. Triển Khai Lab Server

### Chuẩn bị server

```bash
# Cài Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Cài Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:8b

# Clone project
git clone <repo-url>
cd ISIlab_AI
cp .env.example .env
```

### Cấu hình .env cho production

```bash
APP_ENV=production
LOG_LEVEL=WARNING
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

### Chạy

```bash
docker compose up -d --build
```

### Kiểm tra

```bash
curl http://localhost:8000/health
```

## 3. Kết nối Client

Từ các máy lab client, mở browser và truy cập:

```
http://<server-ip>:8000
```

Thay `<server-ip>` bằng IP của lab server trong mạng LAN.
