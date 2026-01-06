"""
إعدادات البوت الرئيسية
Configuration settings for the Telegram Music Bot
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    """إعدادات التطبيق الرئيسية"""
    
    # Telegram Bot Settings
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8436913185:AAHsRxvIzwULvgC_e6Z1cCyCPE1VpQQxWCg')
    
    # YouTube API Settings
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # OpenAI API Settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Audio Settings
    AUDIO_QUALITY = os.getenv('AUDIO_QUALITY', '320')  # kbps
    AUDIO_FORMAT = os.getenv('AUDIO_FORMAT', 'mp3')
    
    # File Management
    TEMP_DIR = os.getenv('TEMP_DIR', './temp')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '50'))  # MB
    CLEANUP_AFTER_SEND = os.getenv('CLEANUP_AFTER_SEND', 'true').lower() == 'true'
    
    # Bot Behavior
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '5'))
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'ar')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # Rate Limiting
    MAX_DOWNLOADS_PER_USER = int(os.getenv('MAX_DOWNLOADS_PER_USER', '10'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # seconds
    
    @classmethod
    def validate_config(cls):
        """التحقق من صحة الإعدادات المطلوبة"""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'YOUTUBE_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"متغيرات البيئة المطلوبة مفقودة: {', '.join(missing_vars)}")
        
        return True

# إعدادات FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': f'-vn -acodec libmp3lame -ab {Config.AUDIO_QUALITY}k'
}

# رسائل البوت
BOT_MESSAGES = {
    'ar': {
        'welcome': '🎵 مرحباً! أرسل لي اسم الأغنية أو رابط YouTube وسأقوم بتحميلها لك',
        'searching': '🔍 جاري البحث عن الأغنية...',
        'downloading': '⬇️ جاري تحميل الأغنية...',
        'processing': '⚙️ جاري معالجة الصوت...',
        'enhancing': '🤖 جاري تحسين البيانات الوصفية...',
        'uploading': '📤 جاري رفع الملف...',
        'success': '✅ تم! إليك أغنيتك',
        'error': '❌ حدث خطأ: {}',
        'not_found': '❌ لم أجد هذه الأغنية',
        'too_long': '❌ الأغنية طويلة جداً (أكثر من {} دقيقة)',
        'help': '''
🎵 *بوت تحميل الموسيقى*

*الأوامر المتاحة:*
/start - بدء البوت
/help - عرض هذه الرسالة
/download <اسم الأغنية> - تحميل أغنية

*كيفية الاستخدام:*
1. أرسل اسم الأغنية أو اسم الفنان
2. أو أرسل رابط YouTube مباشرة
3. انتظر حتى يتم التحميل والمعالجة
4. استمتع بأغنيتك! 🎶

*مثال:*
`Fairuz - Li Beirut`
أو
`https://youtube.com/watch?v=...`
        '''
    }
}
