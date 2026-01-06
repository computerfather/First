"""
البوت الرئيسي لـ Telegram
Main Telegram Bot class
"""

import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TelegramError

from src.bot.handlers import BotHandlers
from config import Config

logger = logging.getLogger(__name__)

class MusicBot:
    """فئة البوت الرئيسية"""
    
    def __init__(self, token: str = None):
        """
        تهيئة البوت
        
        Args:
            token: توكن البوت (اختياري، سيتم أخذه من الإعدادات)
        """
        self.token = token or Config.TELEGRAM_BOT_TOKEN
        if not self.token:
            raise ValueError("توكن Telegram Bot مطلوب")
        
        # إنشاء التطبيق
        self.application = Application.builder().token(self.token).build()
        
        # تهيئة المعالجات
        self.handlers = BotHandlers()
        
        # تسجيل المعالجات
        self._register_handlers()
        
        logger.info("تم تهيئة البوت بنجاح")
    
    def _register_handlers(self):
        """تسجيل معالجات الأوامر والرسائل"""
        try:
            # معالجات الأوامر
            self.application.add_handler(
                CommandHandler("start", self.handlers.start_command)
            )
            
            self.application.add_handler(
                CommandHandler("help", self.handlers.help_command)
            )
            
            self.application.add_handler(
                CommandHandler("download", self.handlers.download_command)
            )
            
            # معالج الرسائل النصية
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, 
                    self.handlers.message_handler
                )
            )
            
            # معالج أزرار الكيبورد
            self.application.add_handler(
                CallbackQueryHandler(self.handlers.button_callback)
            )
            
            # معالج الأخطاء
            self.application.add_error_handler(self.handlers.error_handler)
            
            logger.info("تم تسجيل جميع المعالجات")
            
        except Exception as e:
            logger.error(f"خطأ في تسجيل المعالجات: {e}")
            raise
    
    async def start(self):
        """بدء تشغيل البوت"""
        try:
            logger.info("بدء تشغيل البوت...")
            
            # تهيئة البوت
            await self.application.initialize()
            
            # بدء البوت
            await self.application.start()
            
            # بدء polling
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=['message', 'callback_query']
            )
            
            logger.info("البوت يعمل الآن! اضغط Ctrl+C للإيقاف")
            
            # انتظار إيقاف البوت
            await self.application.updater.idle()
            
        except KeyboardInterrupt:
            logger.info("تم إيقاف البوت بواسطة المستخدم")
        except Exception as e:
            logger.error(f"خطأ في تشغيل البوت: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """إيقاف البوت"""
        try:
            logger.info("إيقاف البوت...")
            
            # إيقاف updater
            if self.application.updater:
                await self.application.updater.stop()
            
            # إيقاف التطبيق
            await self.application.stop()
            
            # تنظيف الموارد
            await self.application.shutdown()
            
            # تنظيف الملفات المؤقتة
            if hasattr(self.handlers, 'downloader'):
                self.handlers.downloader.cleanup_temp_files()
            
            if hasattr(self.handlers, 'audio_processor'):
                self.handlers.audio_processor.cleanup_processed_files()
            
            logger.info("تم إيقاف البوت بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف البوت: {e}")
    
    async def send_message_to_user(self, user_id: int, message: str):
        """
        إرسال رسالة لمستخدم محدد
        
        Args:
            user_id: معرف المستخدم
            message: الرسالة
        """
        try:
            await self.application.bot.send_message(
                chat_id=user_id,
                text=message
            )
            logger.info(f"تم إرسال رسالة للمستخدم {user_id}")
            
        except TelegramError as e:
            logger.error(f"خطأ في إرسال رسالة للمستخدم {user_id}: {e}")
        except Exception as e:
            logger.error(f"خطأ غير متوقع في إرسال الرسالة: {e}")
    
    async def broadcast_message(self, message: str, user_ids: list = None):
        """
        إرسال رسالة جماعية
        
        Args:
            message: الرسالة
            user_ids: قائمة معرفات المستخدمين (اختياري)
        """
        try:
            if not user_ids:
                user_ids = list(self.handlers.usage_stats.keys())
            
            successful_sends = 0
            failed_sends = 0
            
            for user_id in user_ids:
                try:
                    await self.send_message_to_user(user_id, message)
                    successful_sends += 1
                    
                    # تأخير قصير لتجنب rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"فشل إرسال رسالة للمستخدم {user_id}: {e}")
                    failed_sends += 1
            
            logger.info(f"تم إرسال {successful_sends} رسالة، فشل {failed_sends}")
            
        except Exception as e:
            logger.error(f"خطأ في الإرسال الجماعي: {e}")
    
    def get_bot_info(self) -> dict:
        """الحصول على معلومات البوت"""
        try:
            return {
                'bot_username': self.application.bot.username,
                'bot_id': self.application.bot.id,
                'total_users': len(self.handlers.usage_stats),
                'total_downloads': sum(
                    stats.get('downloads', 0) 
                    for stats in self.handlers.usage_stats.values()
                )
            }
        except Exception as e:
            logger.error(f"خطأ في جلب معلومات البوت: {e}")
            return {}
    
    def get_user_stats(self) -> dict:
        """الحصول على إحصائيات المستخدمين"""
        try:
            return {
                'total_users': len(self.handlers.usage_stats),
                'active_users': len([
                    stats for stats in self.handlers.usage_stats.values()
                    if stats.get('downloads', 0) > 0
                ]),
                'total_downloads': sum(
                    stats.get('downloads', 0) 
                    for stats in self.handlers.usage_stats.values()
                ),
                'users_data': self.handlers.usage_stats
            }
        except Exception as e:
            logger.error(f"خطأ في جلب إحصائيات المستخدمين: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """فحص صحة البوت"""
        try:
            # التحقق من اتصال البوت
            bot_info = await self.application.bot.get_me()
            if not bot_info:
                return False
            
            # التحقق من المعالجات
            if not self.handlers:
                return False
            
            # التحقق من الخدمات
            services_status = {
                'youtube_api': hasattr(self.handlers, 'youtube_api'),
                'downloader': hasattr(self.handlers, 'downloader'),
                'audio_processor': hasattr(self.handlers, 'audio_processor'),
                'metadata_tagger': hasattr(self.handlers, 'metadata_tagger'),
                'ai_enhancer': hasattr(self.handlers, 'ai_enhancer')
            }
            
            # التحقق من أن جميع الخدمات متوفرة
            if not all(services_status.values()):
                logger.warning(f"بعض الخدمات غير متوفرة: {services_status}")
                return False
            
            logger.info("فحص صحة البوت: ✅ جميع الخدمات تعمل بشكل طبيعي")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في فحص صحة البوت: {e}")
            return False
    
    async def restart_services(self):
        """إعادة تشغيل الخدمات"""
        try:
            logger.info("إعادة تشغيل الخدمات...")
            
            # إعادة تهيئة المعالجات
            self.handlers = BotHandlers()
            
            # إعادة تسجيل المعالجات
            self._register_handlers()
            
            logger.info("تم إعادة تشغيل الخدمات بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في إعادة تشغيل الخدمات: {e}")
            raise
