# System Architecture

## Overview

The Smart License Plate Recognition system follows a microservices-inspired architecture with a clear separation between frontend, backend, and ML components.

```
+-----------------------------------------------------+
|                    Client Browser                   |
|              React 18 + Material UI                 |
+----------------------+------------------------------+
                       | HTTP / WebSocket
+----------------------v------------------------------+
|                  nginx (port 80)                    |
|           Reverse Proxy + Static Files              |
+----------------------+------------------------------+
                       | HTTP
+----------------------v------------------------------+
|               FastAPI Backend (port 8000)           |
|                                                     |
|  +-------------+  +--------------+  +-----------+  |
|  |   Routes    |  |   Services   |  |  WebSocket|  |
|  |  /plates    |  | PlateService |  |  Handler  |  |
|  |  /dashboard |  | OCRService   |  |           |  |
|  |  /analytics |  | YOLOService  |  |           |  |
|  +------+------+  +------+-------+  +-----------+  |
|         |                |                          |
|  +------v----------------v-----------------------+  |
|  |              SQLAlchemy ORM                   |  |
|  +-------------------------------+---------------+  |
|                                  |                  |
|  +-------------------------------v---------------+  |
|  |             SQLite Database                   |  |
|  |          data/license_plates.db               |  |
|  +-----------------------------------------------+  |
+-----------------------------------------------------+
           |
+----------v------------------------------------------+
|                  ML Pipeline                        |
|  +------------------+   +-------------------------+ |
|  |  YOLOv8 Detector |   |    EasyOCR Engine       | |
|  |  (plate location)|-->|  (text recognition)     | |
|  +------------------+   +-------------------------+ |
|              models/*.pt                            |
+-----------------------------------------------------+
```

## Component Details

### Frontend (React 18)

- **Framework**: React 18 with functional components and hooks
- **UI Library**: Material UI v5 with RTL support
- **Routing**: React Router v6
- **Charts**: Recharts
- **HTTP Client**: Axios with interceptors
- **File Upload**: react-dropzone

### Backend (FastAPI)

- **Framework**: FastAPI with async/await support
- **ORM**: SQLAlchemy 2.0 with async session
- **Database**: SQLite via aiosqlite
- **Validation**: Pydantic v2
- **API Docs**: Auto-generated Swagger/OpenAPI

### ML Pipeline

1. **Image Preprocessing**: OpenCV (resize, normalize)
2. **Plate Detection**: YOLOv8 (bounding box detection)
3. **Plate Cropping**: Extract detected region
4. **OCR**: EasyOCR for Persian/Arabic text
5. **Post-processing**: Province identification, type classification

### Data Flow

```
Image Upload
     |
     v
Validation (size, format)
     |
     v
YOLOv8 Detection
     |
     v
ROI Extraction (crop plate region)
     |
     v
Image Enhancement
     |
     v
EasyOCR Text Recognition
     |
     v
Post-processing (province ID, type detection)
     |
     v
Database Storage
     |
     v
JSON Response
```

## Security

- Non-root Docker container execution
- Input validation on all endpoints
- File type and size validation
- Optional API key authentication
- CORS configuration
- No secrets in code (env vars only)

## Scalability

- Stateless backend (horizontal scaling ready)
- Async I/O throughout
- Connection pooling for database
- Docker Compose for local orchestration
- Kubernetes-ready architecture
