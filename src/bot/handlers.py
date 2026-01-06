"""
معالجات أوامر بوت Telegram
Telegram bot command handlers
"""

import logging
import os
import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.youtube.youtube_api import YouTubeAPI
from src.audio.downloader import AudioDownloader
from src.audio.audio_processor import AudioProcessor
from src.audio.metadata_tagger import MetadataTagger
from src.ai.ai_metadata import AIMetadataEnhancer
from config import Config, BOT_MESSAGES

logger = logging.getLogger(__name__)

class BotHandlers:
    """فئة معالجات أوامر البوت"""
    
    def __init__(self):
        """تهيئة المعالجات"""
        try:
            self.youtube_api = YouTubeAPI()
            self.downloader = AudioDownloader()
            self.audio_processor = AudioProcessor()
            self.metadata_tagger = MetadataTagger()
            self.ai_enhancer = AIMetadataEnhancer()
            
            # إحصائيات الاستخدام
            self.usage_stats = {}
            
            logger.info("تم تهيئة معالجات البوت بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة معالجات البوت: {e}")
            raise
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # تسجيل المستخدم الجديد
            if user_id not in self.usage_stats:
                self.usage_stats[user_id] = {
                    'downloads': 0,
                    'first_use': update.message.date,
                    'username': user.username or user.first_name
                }
                logger.info(f"مستخدم جديد: {user.first_name} ({user_id})")
            
            # رسالة الترحيب
            welcome_text = BOT_MESSAGES['ar']['welcome']
            
            # إنشاء لوحة مفاتيح
            keyboard = [
                [InlineKeyboardButton("📖 المساعدة", callback_data="help")],
                [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالج /start: {e}")
            await update.message.reply_text("❌ حدث خطأ في بدء البوت")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        try:
            help_text = BOT_MESSAGES['ar']['help']
            await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"خطأ في معالج /help: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض المساعدة")
    
    async def download_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /download"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ يرجى إدخال اسم الأغنية أو رابط YouTube\n"
                    "مثال: `/download Fairuz - Li Beirut`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            query = " ".join(context.args)
            await self.process_music_request(update, query)
            
        except Exception as e:
            logger.error(f"خطأ في معالج /download: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الطلب")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        try:
            message_text = update.message.text.strip()
            
            # تجاهل الرسائل الفارغة
            if not message_text:
                return
            
            # التحقق من كونها رابط YouTube أو طلب أغنية
            if self.youtube_api.is_valid_youtube_url(message_text):
                await self.process_music_request(update, message_text)
            else:
                # اعتبارها طلب بحث عن أغنية
                await self.process_music_request(update, message_text)
                
        except Exception as e:
            logger.error(f"خطأ في معالج الرسائل: {e}")
            await update.message.reply_text("❌ حدث خطأ في معالجة الرسالة")
    
    async def process_music_request(self, update: Update, query: str):
        """معالجة طلب تحميل الموسيقى"""
        user_id = update.effective_user.id
        
        try:
            # التحقق من حد التحميل
            if not self._check_rate_limit(user_id):
                await update.message.reply_text(
                    f"❌ لقد تجاوزت الحد المسموح ({Config.MAX_DOWNLOADS_PER_USER} تحميل في الساعة)"
                )
                return
            
            # إرسال رسالة البحث
            status_message = await update.message.reply_text(
                BOT_MESSAGES['ar']['searching']
            )
            
            # البحث عن الفيديو
            video_info = await self._search_video(query, status_message)
            if not video_info:
                await status_message.edit_text(BOT_MESSAGES['ar']['not_found'])
                return
            
            # تحديث الرسالة - التحميل
            await status_message.edit_text(BOT_MESSAGES['ar']['downloading'])
            
            # تحميل الصوت
            download_info = await self._download_audio(video_info, status_message)
            if not download_info:
                await status_message.edit_text("❌ فشل في تحميل الصوت")
                return
            
            # تحديث الرسالة - المعالجة
            await status_message.edit_text(BOT_MESSAGES['ar']['processing'])
            
            # معالجة الصوت
            processed_file = await self._process_audio(download_info['filepath'])
            if not processed_file:
                processed_file = download_info['filepath']
            
            # تحديث الرسالة - تحسين البيانات
            await status_message.edit_text(BOT_MESSAGES['ar']['enhancing'])
            
            # تحسين البيانات الوصفية
            enhanced_metadata = await self._enhance_metadata(video_info)
            
            # إضافة البيانات الوصفية
            await self._add_metadata(processed_file, enhanced_metadata, video_info.get('thumbnail'))
            
            # تحديث الرسالة - الرفع
            await status_message.edit_text(BOT_MESSAGES['ar']['uploading'])
            
            # إرسال الملف
            await self._send_audio_file(update, processed_file, enhanced_metadata, video_info)
            
            # حذف رسالة الحالة
            await status_message.delete()
            
            # تحديث الإحصائيات
            self._update_user_stats(user_id)
            
            # تنظيف الملفات
            await self._cleanup_files([download_info['filepath'], processed_file])
            
        except Exception as e:
            logger.error(f"خطأ في معالجة طلب الموسيقى: {e}")
            try:
                await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
            except:
                pass
    
    async def _search_video(self, query: str, status_message) -> Optional[dict]:
        """البحث عن الفيديو"""
        try:
            if self.youtube_api.is_valid_youtube_url(query):
                # رابط مباشر
                video_info = self.youtube_api.get_video_info(query)
            else:
                # بحث بالاسم
                video_info = self.youtube_api.get_best_match(query)
            
            return video_info
            
        except Exception as e:
            logger.error(f"خطأ في البحث: {e}")
            return None
    
    async def _download_audio(self, video_info: dict, status_message) -> Optional[dict]:
        """تحميل الصوت"""
        try:
            # تحديد اسم ملف مخصص
            custom_filename = f"{video_info.get('title', 'audio')}"
            
            download_info = self.downloader.download_audio(
                video_info['url'], 
                custom_filename=custom_filename
            )
            
            return download_info
            
        except Exception as e:
            logger.error(f"خطأ في التحميل: {e}")
            return None
    
    async def _process_audio(self, file_path: str) -> Optional[str]:
        """معالجة الصوت"""
        try:
            processed_file = self.audio_processor.process_audio_complete(
                file_path,
                normalize=True,
                trim_silence=True
            )
            
            return processed_file
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الصوت: {e}")
            return None
    
    async def _enhance_metadata(self, video_info: dict) -> dict:
        """تحسين البيانات الوصفية"""
        try:
            enhanced = self.ai_enhancer.enhance_metadata(
                video_info.get('title', ''),
                video_info.get('channel', ''),
                video_info.get('description', '')
            )
            
            # إضافة معلومات إضافية
            enhanced.update({
                'album': enhanced.get('title', 'Unknown Album'),
                'year': video_info.get('published_at', '')[:4] if video_info.get('published_at') else '',
                'duration': video_info.get('duration', 0)
            })
            
            return enhanced
            
        except Exception as e:
            logger.error(f"خطأ في تحسين البيانات: {e}")
            # إرجاع بيانات أساسية في حالة الفشل
            return {
                'artist': video_info.get('channel', 'Unknown Artist'),
                'title': video_info.get('title', 'Unknown Title'),
                'album': video_info.get('title', 'Unknown Album')
            }
    
    async def _add_metadata(self, file_path: str, metadata: dict, cover_url: str = None):
        """إضافة البيانات الوصفية"""
        try:
            success = self.metadata_tagger.add_metadata(
                file_path, 
                metadata, 
                cover_url
            )
            
            if success:
                logger.info("تم إضافة البيانات الوصفية بنجاح")
            else:
                logger.warning("فشل في إضافة البيانات الوصفية")
                
        except Exception as e:
            logger.error(f"خطأ في إضافة البيانات الوصفية: {e}")
    
    async def _send_audio_file(self, update: Update, file_path: str, 
                             metadata: dict, video_info: dict):
        """إرسال الملف الصوتي"""
        try:
            # معلومات الملف
            file_size = os.path.getsize(file_path)
            duration = metadata.get('duration', 0)
            
            # التحقق من حجم الملف
            if file_size > 50 * 1024 * 1024:  # 50MB
                await update.message.reply_text("❌ الملف كبير جداً للإرسال")
                return
            
            # إعداد معلومات الصوت
            title = metadata.get('title', 'Unknown')
            artist = metadata.get('artist', 'Unknown Artist')
            
            # إرسال الملف
            with open(file_path, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    duration=int(duration) if duration else None,
                    performer=artist,
                    title=title,
                    caption=f"🎵 **{title}**\n👤 {artist}\n\n✅ {BOT_MESSAGES['ar']['success']}",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            logger.info(f"تم إرسال الملف بنجاح: {title}")
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الملف: {e}")
            await update.message.reply_text("❌ فشل في إرسال الملف")
    
    async def _cleanup_files(self, file_paths: list):
        """تنظيف الملفات"""
        try:
            for file_path in file_paths:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.debug(f"تم حذف الملف: {file_path}")
                    except Exception as e:
                        logger.warning(f"لم يتم حذف الملف {file_path}: {e}")
                        
        except Exception as e:
            logger.error(f"خطأ في تنظيف الملفات: {e}")
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """التحقق من حد التحميل"""
        try:
            if user_id not in self.usage_stats:
                return True
            
            user_stats = self.usage_stats[user_id]
            downloads = user_stats.get('downloads', 0)
            
            return downloads < Config.MAX_DOWNLOADS_PER_USER
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من حد التحميل: {e}")
            return True
    
    def _update_user_stats(self, user_id: int):
        """تحديث إحصائيات المستخدم"""
        try:
            if user_id in self.usage_stats:
                self.usage_stats[user_id]['downloads'] += 1
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الإحصائيات: {e}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أزرار الكيبورد"""
        try:
            query = update.callback_query
            await query.answer()
            
            if query.data == "help":
                help_text = BOT_MESSAGES['ar']['help']
                await query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN)
            
            elif query.data == "stats":
                user_id = update.effective_user.id
                stats = self.usage_stats.get(user_id, {})
                downloads = stats.get('downloads', 0)
                
                stats_text = f"📊 **إحصائياتك:**\n\n🎵 عدد التحميلات: {downloads}\n📅 تاريخ التسجيل: {stats.get('first_use', 'غير معروف')}"
                
                await query.edit_message_text(stats_text, parse_mode=ParseMode.MARKDOWN)
                
        except Exception as e:
            logger.error(f"خطأ في معالج الأزرار: {e}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأخطاء العام"""
        try:
            logger.error(f"خطأ في البوت: {context.error}")
            
            if update and update.message:
                await update.message.reply_text(
                    "❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
                )
                
        except Exception as e:
            logger.error(f"خطأ في معالج الأخطاء: {e}")
