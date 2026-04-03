# Database Schema

## Overview

The system uses SQLite as the database, accessed through SQLAlchemy 2.0 async ORM.

**Database file**: `data/license_plates.db`

---

## Tables

### `plate_detections`

Stores all license plate detection records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique record ID |
| plate_number | VARCHAR(50) | NOT NULL, INDEX | Detected plate text |
| plate_type | VARCHAR(20) | NOT NULL, INDEX | Type: passenger/motorcycle/government/unknown |
| province | VARCHAR(100) | NULLABLE | Province name derived from plate code |
| confidence | FLOAT | NOT NULL | Detection confidence (0.0 - 1.0) |
| image_path | VARCHAR(500) | NULLABLE | Relative path to stored image |
| raw_text | TEXT | NULLABLE | Raw OCR output before post-processing |
| bounding_box | TEXT | NULLABLE | JSON: plate location in image [x1,y1,x2,y2] |
| created_at | DATETIME | DEFAULT NOW | Record creation timestamp |
| updated_at | DATETIME | DEFAULT NOW, ON UPDATE | Last update timestamp |

**Indexes:**
- `idx_plate_number` on `plate_number`
- `idx_plate_type` on `plate_type`
- `idx_created_at` on `created_at`

---

## Province Codes

Iranian license plates use 2-digit province codes:

| Code | Province |
|------|---------|
| 11 | Tehran |
| 22 | Isfahan |
| 33 | Mashhad (Razavi Khorasan) |
| 44 | East Azerbaijan (Tabriz) |
| 55 | Shiraz (Fars) |
| 66 | Ahvaz (Khuzestan) |
| 77 | Kermanshah |

---

## Migrations

The database schema is created automatically on first startup using SQLAlchemy `create_all()`.

For production environments, consider using Alembic for migrations:

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "initial"

# Apply migration
alembic upgrade head
```
