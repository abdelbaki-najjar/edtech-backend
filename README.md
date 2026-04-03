# 🎮 EdTech Tunisia — FastAPI Backend

منصة الألعاب التعليمية للتعليم الابتدائي التونسي 🇹🇳

---

## 🗂️ هيكل المشروع الكامل

```
edtech-backend/
│
├── main.py                    ← نقطة البداية — شغّل من هنا
│
├── core/                      ← إعدادات أساسية
│   ├── config.py              ← قراءة .env والإعدادات
│   ├── database.py            ← اتصال PostgreSQL
│   └── auth.py                ← JWT والمصادقة
│
├── models/                    ← جداول قاعدة البيانات
│   ├── student.py             ← جدول الطلاب
│   ├── session.py             ← جدول جلسات اللعب
│   └── school.py              ← جدول المدارس (B2B)
│
├── routes/                    ← نقاط نهاية API
│   ├── ai.py                  ← /api/ai/* (توليد الألعاب)
│   ├── auth.py                ← /api/auth/* (تسجيل/دخول)
│   ├── students.py            ← /api/students/*
│   ├── sessions.py            ← /api/sessions/*
│   └── analytics.py           ← /api/analytics/* (المعلم)
│
├── services/                  ← منطق الأعمال
│   └── ai_service.py          ← Multi-Agent AI System
│
├── requirements.txt           ← المكتبات
├── .env.example               ← نموذج الإعدادات
└── .env                       ← إعداداتك السرية (لا ترفعه!)
```

---

## ⚡ تشغيل المشروع (خطوة بخطوة)

### 1. تثبيت Python
```bash
# تحقق من الإصدار (يجب 3.11+)
python --version
```

### 2. إنشاء بيئة افتراضية
```bash
cd edtech-backend

# إنشاء
python -m venv venv

# تفعيل (Windows)
venv\Scripts\activate

# تفعيل (Mac/Linux)
source venv/bin/activate
```

### 3. تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### 4. إعداد .env
```bash
cp .env.example .env
# افتح .env وأضف مفاتيحك
```

### 5. تشغيل الـ Backend
```bash
uvicorn main:app --reload
```

### 6. اختبار API
```
افتح: http://localhost:8000
Docs: http://localhost:8000/docs   ← واجهة تفاعلية جاهزة!
```

---

## 🔗 ربط React Frontend بـ FastAPI

في ملف `lib/api.js` في React:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function generateGame(params) {
  const res = await fetch(`${API_URL}/api/ai/generate-game`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("token")}`,
    },
    body: JSON.stringify(params),
  });
  return res.json();
}
```

---

## 🚀 النشر على Railway (أسهل من Heroku)

```bash
# 1. اذهب لـ railway.app وسجّل
# 2. New Project → Deploy from GitHub
# 3. أضف Environment Variables من .env
# 4. أضف PostgreSQL Plugin مجاناً
# رابطك: edtech-api.railway.app ✅
```

---

## 📡 قائمة الـ APIs

| Method | Endpoint                      | الوظيفة              |
|--------|-------------------------------|----------------------|
| POST   | /api/auth/register            | تسجيل طالب جديد     |
| POST   | /api/auth/login               | تسجيل الدخول         |
| POST   | /api/ai/generate-game         | 🤖 توليد لعبة        |
| POST   | /api/ai/generate-worksheet    | 📄 توليد ورقة عمل    |
| POST   | /api/ai/analyze               | 📊 تحليل الأداء      |
| GET    | /api/students/me              | بيانات الطالب        |
| GET    | /api/students/leaderboard     | 🏆 لوحة الشرف        |
| GET    | /api/students/{id}/progress   | تقدم طالب محدد       |
| POST   | /api/sessions/save            | 💾 حفظ نتيجة اللعبة  |
| GET    | /api/analytics/overview       | لوحة المعلم          |
| GET    | /api/analytics/recommendations| توصيات AI            |
