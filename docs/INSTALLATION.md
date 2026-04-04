# Installation Guide

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+ (for Docker installation)
- Python 3.11+ (for manual installation)
- Node.js 18+ and npm 8+ (for frontend manual installation)

---

## Option 1: Docker Installation (Recommended)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/smart-license-plate-recognition.git
cd smart-license-plate-recognition
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed
nano .env
```

### 3. Add ML Model (Optional)

```bash
# Place your YOLOv8 model in the models directory
cp /path/to/your/yolov8_plate.pt models/
```

### 4. Start Services

```bash
docker-compose up -d
```

### 5. Verify

```bash
# Check services are running
docker-compose ps

# Test backend
curl http://localhost:8000/api/health

# Open frontend
open http://localhost:80
```

### Useful Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Remove volumes (reset data)
docker-compose down -v
```

---

## Option 2: Manual Installation

### Backend

#### 1. Navigate to Backend

```bash
cd backend
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
cp ../.env.example .env
# Edit .env with your settings
```

#### 5. Create Directories

```bash
mkdir -p data logs uploads models
```

#### 6. Run Backend

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

#### 1. Navigate to Frontend

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure Environment

```bash
cp .env.example .env.local
# Edit .env.local
# REACT_APP_API_URL=http://localhost:8000
```

#### 4. Run Frontend

```bash
# Development
npm start

# Production build
npm run build
# Serve with nginx or any static server
```

---

## Troubleshooting

### Common Issues

#### Backend fails to start
- Check Python version: `python --version` (must be 3.11+)
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check port 8000 is not in use: `lsof -i :8000`

#### Frontend cannot connect to backend
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check CORS settings in `.env`
- Verify `REACT_APP_API_URL` in frontend `.env.local`

#### Docker build fails
- Ensure Docker daemon is running
- Check disk space: `df -h`
- Try rebuilding: `docker-compose build --no-cache`

#### No plate detected
- Ensure image is clear and well-lit
- Check model file exists in `models/`
- Try with a different image

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Storage | 5 GB | 20+ GB |
| GPU | Not required | CUDA-compatible (for faster inference) |
