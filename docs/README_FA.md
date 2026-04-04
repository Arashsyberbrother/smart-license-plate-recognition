<div dir="rtl">

# سیستم هوشمند تشخیص پلاک خودرو ایران

## معرفی

این پروژه یک سیستم کامل برای تشخیص و خواندن پلاک‌های خودروهای ایرانی است. سیستم از هوش مصنوعی برای پردازش تصاویر استفاده می‌کند و قادر به تشخیص انواع مختلف پلاک‌های ایرانی است.

## ویژگی‌های کلیدی

- **تشخیص خودکار پلاک**: با استفاده از مدل YOLOv8 پلاک را در تصویر پیدا می‌کند
- **خواندن متن پلاک**: با EasyOCR متن فارسی/عربی پلاک را می‌خواند
- **شناسایی استان**: از روی کد پلاک، استان خودرو را تشخیص می‌دهد
- **داشبورد آماری**: نمودارها و آمار تشخیص‌ها
- **تاریخچه**: جستجو و فیلتر در سابقه تشخیص‌ها
- **WebSocket**: پشتیبانی از تشخیص بلادرنگ
- **Docker**: اجرای آسان با Docker Compose

## ساختار پروژه

```
smart-license-plate-recognition/
├── backend/              # سرور بک‌اند FastAPI
│   ├── app/              # اپلیکیشن اصلی
│   ├── routes/           # مسیرهای API
│   ├── services/         # منطق کسب‌وکار
│   ├── models/           # مدل‌های پایگاه داده
│   └── tests/            # تست‌ها
├── frontend/             # رابط کاربری React
│   ├── src/
│   │   ├── components/   # کامپوننت‌های React
│   │   ├── pages/        # صفحات
│   │   └── services/     # سرویس‌های API
│   └── public/
├── models/               # مدل‌های ML
├── docs/                 # مستندات
└── docker-compose.yml    # تنظیمات Docker
```

## نصب و راه‌اندازی

### روش اول: Docker (توصیه‌شده)

```bash
# کلون کردن پروژه
git clone <repository-url>
cd smart-license-plate-recognition

# کپی فایل محیطی
cp .env.example .env

# اجرا با Docker Compose
docker-compose up -d
```

### روش دوم: نصب دستی

#### بک‌اند

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```

#### فرانت‌اند

```bash
cd frontend
npm install
npm start
```

## API

مستندات کامل API در آدرس `http://localhost:8000/docs` قابل دسترس است.

## پلاک‌های پشتیبانی‌شده

| نوع | فرمت | مثال |
|-----|------|------|
| سواری | ۲ رقم - حرف - ۳ رقم - ۲ رقم استان | ۱۲ ب ۳۴۵ - ۱۱ |
| موتورسیکلت | فرمت مخصوص | --- |
| دولتی | فرمت مخصوص | --- |

## مشارکت

لطفاً قبل از ارسال Pull Request، فایل [CONTRIBUTING.md](CONTRIBUTING.md) را مطالعه کنید.

## مجوز

این پروژه تحت مجوز MIT منتشر شده است.

</div>
