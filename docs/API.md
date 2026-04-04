# API Documentation

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

Optional API key authentication. Pass the key in the header:

```
X-API-Key: your-api-key
```

---

## Endpoints

### Health Check

#### `GET /api/health`

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

---

### Plate Detection

#### `POST /api/plates/detect`

Detect and recognize a license plate from an uploaded image.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file: jpg, png, bmp, webp)

**Response (200):**
```json
{
  "id": 42,
  "plate_number": "12\u062834511",
  "plate_type": "passenger",
  "province": "\u062a\u0647\u0631\u0627\u0646",
  "confidence": 0.94,
  "image_path": "uploads/uuid.jpg",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error (422):**
```json
{
  "detail": "No license plate detected in the image"
}
```

---

### List Plates

#### `GET /api/plates`

Get a paginated list of detected plates.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | int | 0 | Records to skip |
| limit | int | 20 | Max records to return |
| plate_number | string | - | Filter by plate number |
| plate_type | string | - | Filter by type (passenger/motorcycle/government) |

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "plate_number": "12\u062834511",
      "plate_type": "passenger",
      "province": "\u062a\u0647\u0631\u0627\u0646",
      "confidence": 0.94,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

---

### Get Plate by ID

#### `GET /api/plates/{id}`

Get details of a specific plate record.

**Path Parameters:**
- `id` (int): Plate record ID

**Response (200):** Same as single plate object above.

**Error (404):**
```json
{
  "detail": "Plate not found"
}
```

---

### Delete Plate

#### `DELETE /api/plates/{id}`

Delete a plate record.

**Path Parameters:**
- `id` (int): Plate record ID

**Response (200):**
```json
{
  "message": "Plate deleted successfully"
}
```

---

### Dashboard Statistics

#### `GET /api/dashboard/stats`

Get summary statistics for the dashboard.

**Response (200):**
```json
{
  "total_detections": 1500,
  "today_detections": 25,
  "success_rate": 0.92,
  "avg_confidence": 0.88,
  "most_common_province": "\u062a\u0647\u0631\u0627\u0646"
}
```

---

### Daily Analytics

#### `GET /api/analytics/daily`

Get daily detection counts.

**Query Parameters:**
- `days` (int, default: 7): Number of days to include

**Response (200):**
```json
[
  {"date": "2024-01-15", "count": 45},
  {"date": "2024-01-14", "count": 38}
]
```

---

### Distribution Analytics

#### `GET /api/analytics/distribution`

Get plate distribution by type and province.

**Response (200):**
```json
{
  "by_type": {
    "passenger": 1200,
    "motorcycle": 200,
    "government": 100
  },
  "by_province": {
    "\u062a\u0647\u0631\u0627\u0646": 450,
    "\u0627\u0635\u0641\u0647\u0627\u0646": 200,
    "\u0645\u0634\u0647\u062f": 180
  }
}
```

---

### WebSocket

#### `WS /ws`

Real-time WebSocket connection for live updates.

**Messages Received:**
```json
{
  "type": "detection",
  "data": {
    "plate_number": "12\u062834511",
    "confidence": 0.94
  }
}
```

---

## Error Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request / Invalid input |
| 401 | Unauthorized (invalid API key) |
| 404 | Not found |
| 422 | Unprocessable entity / No plate detected |
| 500 | Internal server error |
