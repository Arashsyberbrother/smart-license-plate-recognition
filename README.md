<div dir="rtl">

# 🚗 سیستم هوشمند تشخیص پلاک خودرو ایران

</div>

# Smart Iranian License Plate Recognition System

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

<div dir="rtl">

## معرفی

این سیستم یک راه‌حل هوشمند برای تشخیص و خواندن پلاک‌های خودروهای ایرانی است. با استفاده از مدل YOLOv8 برای تشخیص پلاک و EasyOCR برای خواندن متن، این سیستم قادر است انواع پلاک‌های ایرانی (سواری، موتورسیکلت، دولتی) را با دقت بالا شناسایی کند.

## ویژگی‌ها

- 🔍 تشخیص خودکار پلاک با YOLOv8
- 📝 خواندن متن پلاک با EasyOCR
- 🗺️ شناسایی استان از روی کد پلاک
- 📊 داشبورد آماری و تحلیلی
- 📜 تاریخچه تشخیص‌ها با قابلیت جستجو
- ⚡ پشتیبانی از WebSocket برای تشخیص بلادرنگ
- 🐳 قابلیت اجرا با Docker

</div>

## Features

- 🔍 Automatic plate detection using YOLOv8
- 📝 OCR text reading with EasyOCR (Persian/Arabic support)
- 🗺️ Province identification from plate codes
- 📊 Analytics dashboard with charts
- 📜 Detection history with search and pagination
- ⚡ Real-time WebSocket support
- 🐳 Docker and Docker Compose ready
- 🔒 Optional API key authentication
- 📱 Responsive RTL UI with Material UI

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI 0.109 |
| Database | SQLite + SQLAlchemy 2.0 |
| ML Detection | YOLOv8 (Ultralytics) |
| OCR Engine | EasyOCR 1.7 |
| Frontend | React 18 + Material UI 5 |
| Charts | Recharts |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/smart-license-plate-recognition.git
cd smart-license-plate-recognition

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Manual Installation

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env

# Create required directories
mkdir -p data logs uploads models

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Start development server
npm start
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/plates/detect` | Detect plate in image |
| GET | `/api/plates` | List all detected plates |
| GET | `/api/plates/{id}` | Get plate by ID |
| DELETE | `/api/plates/{id}` | Delete plate record |
| GET | `/api/dashboard/stats` | Get dashboard statistics |
| GET | `/api/analytics/daily` | Daily detection analytics |
| GET | `/api/analytics/distribution` | Plate type distribution |
| GET | `/api/health` | Health check |
| WS | `/ws` | WebSocket endpoint |

## Project Structure

```
smart-license-plate-recognition/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── config.py        # Configuration
│   │   └── database.py      # Database setup
│   ├── routes/              # API routes
│   ├── services/            # Business logic
│   ├── models/              # Database models
│   ├── tests/               # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── styles/          # CSS styles
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── models/                  # ML model files
├── docs/                    # Documentation
├── .github/workflows/       # CI/CD
├── docker-compose.yml
└── README.md
```

## Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
