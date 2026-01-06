#!/usr/bin/env python3
"""
ملف التشغيل الرئيسي لبوت تحميل الموسيقى من Telegram
Main entry point for Telegram Music Bot

هذا البوت يقوم بـ:
- البحث في YouTube باستخدام API
- تحميل الصوت بجودة عالية باستخدام yt-dlp
- معالجة الصوت باستخدام FFmpeg
- تحسين البيانات الوصفية باستخدام الذكاء الاصطناعي
- إضافة البيانات والغلاف للملف باستخدام Mutagen
- إرسال الملف النهائي عبر Telegram

الاستخدام:
    python main.py

المتطلبات:
    - Python 3.8+
    - FFmpeg مثبت على النظام
    - مفاتيح API (Telegram, YouTube, OpenAI)
"""

import asyncio
import signal
import sys
import os
from pathlib import Path

# إضافة مجلد src إلى مسار Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.bot.telegram_bot import MusicBot
from src.utils.logger import setup_logger, get_bot_logger
from src.utils.validators import DataValidator
from src.utils.file_manager import get_file_manager
from config import Config

# إعداد المسجل الرئيسي
logger = setup_logger('TelegramMusicBot')
bot_logger = get_bot_logger()

class BotManager:
    """مدير البوت الرئيسي"""
    
    def __init__(self):
        self.bot = None
        self.running = False
        self.file_manager = get_file_manager()
    
    async def startup_checks(self) -> bool:
        """فحوصات بدء التشغيل"""
        try:
            logger.info("🔍 بدء فحوصات النظام...")
            
            # التحقق من صحة الإعدادات
            config_errors = DataValidator.validate_config()
            if config_errors:
                logger.error("❌ أخطاء في الإعدادات:")
                for error in config_errors:
                    logger.error(f"  - {error}")
                return False
            
            logger.info("✅ الإعدادات صحيحة")
            
            # التحقق من توفر FFmpeg
            try:
                import subprocess
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, timeout=10)
                if result.returncode == 0:
                    logger.info("✅ FFmpeg متوفر")
                else:
                    logger.error("❌ FFmpeg غير متوفر أو لا يعمل")
                    return False
            except Exception as e:
                logger.error(f"❌ خطأ في التحقق من FFmpeg: {e}")
                return False
            
            # التحقق من مجلد الملفات المؤقتة
            if not os.path.exists(Config.TEMP_DIR):
                try:
                    os.makedirs(Config.TEMP_DIR, exist_ok=True)
                    logger.info(f"✅ تم إنشاء مجلد الملفات المؤقتة: {Config.TEMP_DIR}")
                except Exception as e:
                    logger.error(f"❌ لا يمكن إنشاء مجلد الملفات المؤقتة: {e}")
                    return False
            else:
                logger.info("✅ مجلد الملفات المؤقتة موجود")
            
            # تنظيف الملفات القديمة
            cleaned_files = self.file_manager.cleanup_old_files()
            if cleaned_files > 0:
                logger.info(f"🧹 تم تنظيف {cleaned_files} ملف قديم")
            
            logger.info("✅ جميع الفحوصات نجحت")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في فحوصات بدء التشغيل: {e}")
            return False
    
    async def initialize_bot(self) -> bool:
        """تهيئة البوت"""
        try:
            logger.info("🤖 تهيئة البوت...")
            
            # إنشاء البوت
            self.bot = MusicBot(Config.TELEGRAM_BOT_TOKEN)
            
            # فحص صحة البوت
            if await self.bot.health_check():
                logger.info("✅ البوت جاهز للعمل")
                return True
            else:
                logger.error("❌ فشل في فحص صحة البوت")
                return False
                
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة البوت: {e}")
            return False
    
    async def start_bot(self):
        """بدء تشغيل البوت"""
        try:
            if not await self.startup_checks():
                logger.error("❌ فشلت فحوصات بدء التشغيل")
                return False
            
            if not await self.initialize_bot():
                logger.error("❌ فشل في تهيئة البوت")
                return False
            
            # تسجيل معلومات البوت
            bot_info = self.bot.get_bot_info()
            logger.info("🎵 بوت تحميل الموسيقى")
            logger.info("=" * 50)
            logger.info(f"🤖 اسم البوت: @{bot_info.get('bot_username', 'غير معروف')}")
            logger.info(f"🆔 معرف البوت: {bot_info.get('bot_id', 'غير معروف')}")
            logger.info(f"👥 عدد المستخدمين: {bot_info.get('total_users', 0)}")
            logger.info(f"📥 إجمالي التحميلات: {bot_info.get('total_downloads', 0)}")
            logger.info("=" * 50)
            
            # بدء البوت
            self.running = True
            bot_logger.info("بدء تشغيل البوت")
            
            await self.bot.start()
            
        except KeyboardInterrupt:
            logger.info("⏹️ تم إيقاف البوت بواسطة المستخدم")
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """إيقاف البوت وتنظيف الموارد"""
        try:
            logger.info("⏹️ إيقاف البوت...")
            self.running = False
            
            if self.bot:
                await self.bot.stop()
            
            # تنظيف الملفات المؤقتة
            logger.info("🧹 تنظيف الملفات المؤقتة...")
            cleaned_files = self.file_manager.cleanup_all_temp_files()
            if cleaned_files > 0:
                logger.info(f"🗑️ تم حذف {cleaned_files} ملف مؤقت")
            
            # عرض إحصائيات التشغيل
            stats = bot_logger.get_stats()
            logger.info("📊 إحصائيات التشغيل:")
            logger.info(f"  ⏱️ مدة التشغيل: {stats['runtime_str']}")
            logger.info(f"  ℹ️ رسائل معلوماتية: {stats['info_count']}")
            logger.info(f"  ⚠️ تحذيرات: {stats['warning_count']}")
            logger.info(f"  ❌ أخطاء: {stats['error_count']}")
            
            logger.info("✅ تم إيقاف البوت بنجاح")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إيقاف البوت: {e}")

def setup_signal_handlers(bot_manager: BotManager):
    """إعداد معالجات الإشارات"""
    def signal_handler(signum, frame):
        logger.info(f"📡 تم استلام إشارة {signum}")
        if bot_manager.running:
            logger.info("⏹️ إيقاف البوت...")
            # إنشاء مهمة إيقاف في حلقة الأحداث
            loop = asyncio.get_event_loop()
            loop.create_task(bot_manager.shutdown())
    
    # تسجيل معالجات الإشارات
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    if hasattr(signal, 'SIGHUP'):  # Unix only
        signal.signal(signal.SIGHUP, signal_handler)

def print_banner():
    """طباعة شعار البوت"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎵 بوت تحميل الموسيقى 🎵                    ║
║                   Telegram Music Bot                        ║
╠══════════════════════════════════════════════════════════════╣
║  🔍 البحث في YouTube                                         ║
║  ⬇️ تحميل عالي الجودة                                        ║
║  ⚙️ معالجة متقدمة للصوت                                      ║
║  🤖 تحسين البيانات بالذكاء الاصطناعي                         ║
║  🏷️ إضافة البيانات الوصفية والأغلفة                          ║
║  📤 إرسال مباشر عبر Telegram                                ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """التحقق من إصدار Python"""
    if sys.version_info < (3, 8):
        print("❌ يتطلب Python 3.8 أو أحدث")
        print(f"الإصدار الحالي: {sys.version}")
        sys.exit(1)

async def main():
    """الدالة الرئيسية"""
    try:
        # طباعة الشعار
        print_banner()
        
        # التحقق من إصدار Python
        check_python_version()
        
        # إنشاء مدير البوت
        bot_manager = BotManager()
        
        # إعداد معالجات الإشارات
        setup_signal_handlers(bot_manager)
        
        # بدء البوت
        await bot_manager.start_bot()
        
    except Exception as e:
        logger.error(f"❌ خطأ في الدالة الرئيسية: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # تشغيل البوت
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ فادح: {e}")
        sys.exit(1)
