"""
وحدة تحميل الصوت باستخدام yt-dlp
Audio downloader module using yt-dlp
"""

import os
import logging
import tempfile
from typing import Optional, Dict, Any
import yt_dlp
from config import Config

logger = logging.getLogger(__name__)

class AudioDownloader:
    """فئة لتحميل الصوت من YouTube"""
    
    def __init__(self, temp_dir: str = None):
        """
        تهيئة محمل الصوت
        
        Args:
            temp_dir: مجلد الملفات المؤقتة
        """
        self.temp_dir = temp_dir or Config.TEMP_DIR
        self._ensure_temp_dir()
        
        # إعدادات yt-dlp
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': Config.AUDIO_QUALITY,
            'noplaylist': True,
            'no_warnings': False,
            'quiet': False,
            'verbose': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': Config.AUDIO_QUALITY,
            }],
            'postprocessor_args': [
                '-ar', '44100',  # Sample rate
                '-ac', '2',      # Stereo
            ],
        }
    
    def _ensure_temp_dir(self):
        """التأكد من وجود مجلد الملفات المؤقتة"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)
            logger.info(f"تم إنشاء مجلد الملفات المؤقتة: {self.temp_dir}")
    
    def download_audio(self, video_url: str, custom_filename: str = None) -> Optional[Dict[str, Any]]:
        """
        تحميل الصوت من YouTube
        
        Args:
            video_url: رابط الفيديو
            custom_filename: اسم ملف مخصص
            
        Returns:
            معلومات الملف المحمل أو None في حالة الفشل
        """
        try:
            logger.info(f"بدء تحميل الصوت من: {video_url}")
            
            # تخصيص اسم الملف إذا تم توفيره
            if custom_filename:
                safe_filename = self._sanitize_filename(custom_filename)
                self.ydl_opts['outtmpl'] = os.path.join(
                    self.temp_dir, 
                    f"{safe_filename}.%(ext)s"
                )
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # جلب معلومات الفيديو أولاً
                info = ydl.extract_info(video_url, download=False)
                
                # التحقق من مدة الفيديو
                duration = info.get('duration', 0)
                if duration > 600:  # أكثر من 10 دقائق
                    logger.warning(f"الفيديو طويل جداً: {duration} ثانية")
                    return None
                
                # التحقق من حجم الملف المتوقع
                filesize = info.get('filesize') or info.get('filesize_approx', 0)
                if filesize > Config.MAX_FILE_SIZE * 1024 * 1024:  # تحويل إلى بايت
                    logger.warning(f"الملف كبير جداً: {filesize} بايت")
                    return None
                
                # تحميل الملف
                ydl.download([video_url])
                
                # البحث عن الملف المحمل
                downloaded_file = self._find_downloaded_file(info)
                
                if downloaded_file and os.path.exists(downloaded_file):
                    file_info = {
                        'filepath': downloaded_file,
                        'filename': os.path.basename(downloaded_file),
                        'title': info.get('title', 'Unknown'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'duration': duration,
                        'filesize': os.path.getsize(downloaded_file),
                        'thumbnail': info.get('thumbnail'),
                        'description': info.get('description', ''),
                        'upload_date': info.get('upload_date'),
                        'view_count': info.get('view_count', 0)
                    }
                    
                    logger.info(f"تم تحميل الملف بنجاح: {downloaded_file}")
                    return file_info
                else:
                    logger.error("لم يتم العثور على الملف المحمل")
                    return None
                    
        except yt_dlp.DownloadError as e:
            logger.error(f"خطأ في تحميل الفيديو: {e}")
            return None
        except Exception as e:
            logger.error(f"خطأ غير متوقع في التحميل: {e}")
            return None
    
    def _find_downloaded_file(self, info: Dict) -> Optional[str]:
        """البحث عن الملف المحمل"""
        # محاولة العثور على الملف باستخدام عدة طرق
        possible_extensions = ['mp3', 'm4a', 'webm', 'opus']
        base_filename = self._sanitize_filename(info.get('title', 'audio'))
        
        for ext in possible_extensions:
            filepath = os.path.join(self.temp_dir, f"{base_filename}.{ext}")
            if os.path.exists(filepath):
                return filepath
        
        # البحث في جميع الملفات الموجودة
        for filename in os.listdir(self.temp_dir):
            if any(ext in filename.lower() for ext in possible_extensions):
                filepath = os.path.join(self.temp_dir, filename)
                # التحقق من أن الملف تم إنشاؤه حديثاً
                if os.path.getctime(filepath) > (os.time.time() - 300):  # آخر 5 دقائق
                    return filepath
        
        return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """تنظيف اسم الملف من الأحرف غير المسموحة"""
        import re
        
        # إزالة الأحرف غير المسموحة
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # إزالة المسافات الزائدة
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # تحديد الطول الأقصى
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized or 'audio'
    
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """جلب معلومات الفيديو بدون تحميل"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return {
                    'title': info.get('title'),
                    'uploader': info.get('uploader'),
                    'duration': info.get('duration'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail'),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date')
                }
        except Exception as e:
            logger.error(f"خطأ في جلب معلومات الفيديو: {e}")
            return None
    
    def cleanup_temp_files(self, keep_recent: bool = False):
        """تنظيف الملفات المؤقتة"""
        try:
            if not os.path.exists(self.temp_dir):
                return
            
            current_time = os.time.time()
            cleaned_count = 0
            
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                
                if os.path.isfile(filepath):
                    # إذا كان keep_recent=True، احتفظ بالملفات الحديثة (آخر ساعة)
                    if keep_recent:
                        file_age = current_time - os.path.getctime(filepath)
                        if file_age < 3600:  # أقل من ساعة
                            continue
                    
                    try:
                        os.remove(filepath)
                        cleaned_count += 1
                    except OSError as e:
                        logger.warning(f"لم يتم حذف الملف {filepath}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"تم تنظيف {cleaned_count} ملف مؤقت")
                
        except Exception as e:
            logger.error(f"خطأ في تنظيف الملفات المؤقتة: {e}")
    
    def is_supported_url(self, url: str) -> bool:
        """التحقق من دعم الرابط"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                ydl.extract_info(url, download=False)
                return True
        except:
            return False
