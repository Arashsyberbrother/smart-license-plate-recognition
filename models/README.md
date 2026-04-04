# Models Directory

This directory stores ML model files for license plate detection and recognition.

## Required Models

### YOLOv8 License Plate Detection Model

Place your YOLOv8 model file here as `yolov8_plate.pt`.

#### Option 1: Download Pre-trained Model

```bash
# Using ultralytics CLI
pip install ultralytics
yolo export model=yolov8n.pt format=pytorch

# Or download a custom plate detection model
wget -O models/yolov8_plate.pt <model_url>
```

#### Option 2: Train Your Own Model

```bash
# Install ultralytics
pip install ultralytics

# Train on your dataset
yolo train data=plate_dataset.yaml model=yolov8n.pt epochs=100 imgsz=640
```

#### Option 3: Use Default YOLOv8 (Fallback)

The system will fall back to the standard YOLOv8 object detection model if no custom model is found.

## EasyOCR

EasyOCR models are downloaded automatically on first use. They will be cached in `~/.EasyOCR/`.

## File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PyTorch | `.pt`, `.pth` | Native format |
| ONNX | `.onnx` | Cross-platform |

## Notes

- Model files (`.pt`, `.onnx`, `.bin`) are ignored by git (see `.gitignore`)
- Keep this README and `.gitkeep` file tracked
- Minimum recommended model: YOLOv8n (nano) for speed
- Recommended for production: YOLOv8s (small) or YOLOv8m (medium)
