# 🎵 بوت تحميل الموسيقى من Telegram

بوت Telegram احترافي لتحميل الموسيقى من YouTube مع تحسين البيانات الوصفية باستخدام الذكاء الاصطناعي.

## ✨ المميزات

- 🔍 **البحث الذكي**: البحث في YouTube باستخدام API الرسمي
- ⬇️ **تحميل عالي الجودة**: استخدام yt-dlp لتحميل الصوت بجودة 320kbps
- ⚙️ **معالجة متقدمة**: معالجة الصوت باستخدام FFmpeg (تطبيع، إزالة الصمت)
- 🤖 **ذكاء اصطناعي**: تحسين البيانات الوصفية باستخدام GPT
- 🏷️ **بيانات وصفية كاملة**: إضافة اسم الفنان، الأغنية، والغلاف تلقائياً
- 📱 **واجهة سهلة**: أوامر بسيطة وواجهة عربية
- 🛡️ **آمان وموثوقية**: معالجة أخطاء شاملة وتنظيف تلقائي للملفات

## 🚀 التثبيت السريع

### المتطلبات الأساسية

- Python 3.8 أو أحدث
- FFmpeg مثبت على النظام
- مفاتيح API (Telegram Bot, YouTube Data API, OpenAI API)

### 1. تحميل المشروع

```bash
git clone https://github.com/your-username/telegram-music-bot.git
cd telegram-music-bot
```

### 2. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 3. تثبيت FFmpeg

#### على Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### على macOS:
```bash
brew install ffmpeg
```

#### على Windows:
قم بتحميل FFmpeg من [الموقع الرسمي](https://ffmpeg.org/download.html) وإضافته إلى PATH.

### 4. إعداد متغيرات البيئة

انسخ ملف `.env.example` إلى `.env` وقم بتعديل القيم:

```bash
cp .env.example .env
```

قم بتعديل الملف `.env`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# YouTube API Configuration  
YOUTUBE_API_KEY=your_youtube_api_key_here

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Audio Settings
AUDIO_QUALITY=320
AUDIO_FORMAT=mp3

# File Management
TEMP_DIR=./temp
MAX_FILE_SIZE=50
CLEANUP_AFTER_SEND=true

# Bot Behavior
MAX_SEARCH_RESULTS=5
DEFAULT_LANGUAGE=ar

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Rate Limiting
MAX_DOWNLOADS_PER_USER=10
RATE_LIMIT_WINDOW=3600
```

### 5. تشغيل البوت

```bash
python main.py
```

## 🔑 الحصول على مفاتيح API

### Telegram Bot Token

1. ابحث عن [@BotFather](https://t.me/botfather) في Telegram
2. أرسل `/newbot` وتابع التعليمات
3. احفظ التوكن الذي ستحصل عليه

### YouTube Data API Key

1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/)
2. أنشئ مشروع جديد أو اختر مشروع موجود
3. فعّل YouTube Data API v3
4. أنشئ مفتاح API وقم بتقييده لـ YouTube Data API

### OpenAI API Key

1. اذهب إلى [OpenAI Platform](https://platform.openai.com/)
2. أنشئ حساب أو سجل دخول
3. اذهب إلى API Keys وأنشئ مفتاح جديد

## 📱 كيفية الاستخدام

### الأوامر المتاحة

- `/start` - بدء البوت وعرض الترحيب
- `/help` - عرض المساعدة والتعليمات
- `/download <اسم الأغنية>` - تحميل أغنية محددة

### طرق البحث

#### 1. البحث بالاسم
```
Fairuz - Li Beirut
```

#### 2. رابط YouTube مباشر
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

#### 3. رابط مختصر
```
https://youtu.be/dQw4w9WgXcQ
```

### مثال على الاستخدام

1. ابدأ محادثة مع البوت
2. أرسل `/start` للترحيب
3. أرسل اسم الأغنية: `محمد عبده - أبعد من الشوق`
4. انتظر حتى يتم التحميل والمعالجة
5. استلم الملف مع البيانات الوصفية كاملة!

## 🏗️ بنية المشروع

```
telegram-music-bot/
├── src/                          # الكود المصدري
│   ├── bot/                      # بوت Telegram
│   │   ├── __init__.py
│   │   ├── telegram_bot.py       # البوت الرئيسي
│   │   └── handlers.py           # معالجات الأوامر
│   ├── youtube/                  # وحدة YouTube
│   │   ├── __init__.py
│   │   └── youtube_api.py        # YouTube API
│   ├── audio/                    # معالجة الصوت
│   │   ├── __init__.py
│   │   ├── downloader.py         # تحميل الصوت
│   │   ├── audio_processor.py    # معالجة FFmpeg
│   │   └── metadata_tagger.py    # إضافة البيانات
│   ├── ai/                       # الذكاء الاصطناعي
│   │   ├── __init__.py
│   │   └── ai_metadata.py        # تحسين البيانات
│   └── utils/                    # أدوات مساعدة
│       ├── __init__.py
│       ├── logger.py             # نظام التسجيل
│       ├── validators.py         # التحقق من البيانات
│       └── file_manager.py       # إدارة الملفات
├── config.py                     # إعدادات التطبيق
├── main.py                       # ملف التشغيل الرئيسي
├── requirements.txt              # متطلبات Python
├── .env.example                  # مثال متغيرات البيئة
├── .gitignore                    # ملفات Git المتجاهلة
└── README.md                     # هذا الملف
```

## ⚙️ الإعدادات المتقدمة

### إعدادات الصوت

```python
# في config.py
AUDIO_QUALITY = '320'        # جودة الصوت (kbps)
AUDIO_FORMAT = 'mp3'         # صيغة الصوت
MAX_FILE_SIZE = 50           # الحد الأقصى لحجم الملف (MB)
```

### إعدادات الذكاء الاصطناعي

```python
OPENAI_MODEL = 'gpt-3.5-turbo'    # نموذج GPT
```

### إعدادات التحكم في المعدل

```python
MAX_DOWNLOADS_PER_USER = 10       # عدد التحميلات المسموح لكل مستخدم
RATE_LIMIT_WINDOW = 3600          # نافزة زمنية (ثانية)
```

## 🔧 استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. خطأ "FFmpeg not found"
```bash
# تأكد من تثبيت FFmpeg
ffmpeg -version

# إذا لم يكن مثبت، قم بتثبيته
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

#### 2. خطأ في YouTube API
- تأكد من صحة مفتاح YouTube API
- تأكد من تفعيل YouTube Data API v3
- تحقق من حدود الاستخدام

#### 3. خطأ في OpenAI API
- تأكد من صحة مفتاح OpenAI API
- تحقق من رصيد الحساب
- تأكد من صحة اسم النموذج

#### 4. مشاكل الأذونات
```bash
# تأكد من أذونات مجلد الملفات المؤقتة
chmod 755 ./temp
```

### تسجيل الأحداث

يتم حفظ السجلات في:
- `bot.log` - جميع الأحداث
- `bot_errors.log` - الأخطاء فقط

لعرض السجلات المباشرة:
```bash
tail -f bot.log
```

## 🚀 النشر

### النشر على خادم Linux

1. انسخ المشروع إلى الخادم
2. ثبت المتطلبات
3. أنشئ خدمة systemd:

```bash
sudo nano /etc/systemd/system/telegram-music-bot.service
```

```ini
[Unit]
Description=Telegram Music Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/telegram-music-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. فعّل وابدأ الخدمة:
```bash
sudo systemctl enable telegram-music-bot
sudo systemctl start telegram-music-bot
```

### النشر باستخدام Docker

```dockerfile
FROM python:3.9-slim

# تثبيت FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# نسخ الملفات
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# تشغيل البوت
CMD ["python", "main.py"]
```

```bash
docker build -t telegram-music-bot .
docker run -d --name music-bot telegram-music-bot
```

## 🤝 المساهمة

نرحب بالمساهمات! يرجى:

1. عمل Fork للمشروع
2. إنشاء branch جديد للميزة
3. إجراء التغييرات مع اختبارها
4. إرسال Pull Request

### إرشادات المساهمة

- اتبع نمط الكود الموجود
- أضف تعليقات باللغة العربية
- اختبر التغييرات قبل الإرسال
- حدث التوثيق عند الحاجة

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT. راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 🙏 شكر وتقدير

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - مكتبة Telegram Bot
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - تحميل الفيديوهات
- [FFmpeg](https://ffmpeg.org/) - معالجة الصوت والفيديو
- [OpenAI](https://openai.com/) - الذكاء الاصطناعي
- [Mutagen](https://github.com/quodlibet/mutagen) - معالجة البيانات الوصفية

## 📞 الدعم

إذا واجهت أي مشاكل أو لديك أسئلة:

1. تحقق من [الأسئلة الشائعة](#-استكشاف-الأخطاء)
2. ابحث في [Issues](https://github.com/your-username/telegram-music-bot/issues)
3. أنشئ Issue جديد مع تفاصيل المشكلة

---

**تم تطويره بـ ❤️ للمجتمع العربي**
