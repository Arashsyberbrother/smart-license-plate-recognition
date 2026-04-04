# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added
- Initial release of Smart Iranian License Plate Recognition system
- FastAPI backend with async SQLAlchemy database support
- React 18 frontend with Material UI components
- YOLOv8-based license plate detection
- EasyOCR-based text recognition for Persian/Arabic characters
- Real-time WebSocket support for live detection updates
- RESTful API for plate detection, history, and analytics
- Docker and Docker Compose support for easy deployment
- Dashboard with statistics and charts
- Plate history with search, filter, and pagination
- Support for Iranian passenger, motorcycle, and government plates
- Province identification from plate codes
- Confidence scoring for detections
- Comprehensive API documentation
- GitHub Actions CI/CD workflows
- Bilingual (Persian/English) documentation

### Security
- Non-root Docker container execution
- Input validation and sanitization
- Optional API key authentication
- CORS configuration
