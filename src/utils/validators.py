"""
وحدة التحقق من صحة البيانات
Data validation utilities
"""

import re
import os
import logging
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """استثناء خطأ التحقق من الصحة"""
    pass

class DataValidator:
    """فئة للتحقق من صحة البيانات"""
    
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """
        التحقق من صحة رابط YouTube
        
        Args:
            url: الرابط المراد التحقق منه
            
        Returns:
            True إذا كان الرابط صحيحاً
        """
        if not url or not isinstance(url, str):
            return False
        
        youtube_patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in youtube_patterns:
            if re.search(pattern, url):
                return True
        
        return False
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        استخراج معرف الفيديو من رابط YouTube
        
        Args:
            url: رابط YouTube
            
        Returns:
            معرف الفيديو أو None
        """
        if not DataValidator.is_valid_youtube_url(url):
            return None
        
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def is_valid_search_query(query: str) -> bool:
        """
        التحقق من صحة استعلام البحث
        
        Args:
            query: استعلام البحث
            
        Returns:
            True إذا كان الاستعلام صحيحاً
        """
        if not query or not isinstance(query, str):
            return False
        
        # إزالة المسافات
        query = query.strip()
        
        # التحقق من الطول
        if len(query) < 2 or len(query) > 200:
            return False
        
        # التحقق من الأحرف المسموحة
        allowed_pattern = r'^[a-zA-Z0-9\u0600-\u06FF\s\-_.,!?()]+$'
        if not re.match(allowed_pattern, query):
            return False
        
        return True
    
    @staticmethod
    def is_valid_file_path(file_path: str) -> bool:
        """
        التحقق من صحة مسار الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            True إذا كان المسار صحيحاً
        """
        if not file_path or not isinstance(file_path, str):
            return False
        
        try:
            # التحقق من وجود الملف
            if not os.path.exists(file_path):
                return False
            
            # التحقق من أنه ملف وليس مجلد
            if not os.path.isfile(file_path):
                return False
            
            # التحقق من إمكانية القراءة
            if not os.access(file_path, os.R_OK):
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def is_valid_audio_file(file_path: str) -> bool:
        """
        التحقق من صحة ملف الصوت
        
        Args:
            file_path: مسار ملف الصوت
            
        Returns:
            True إذا كان ملف صوت صحيح
        """
        if not DataValidator.is_valid_file_path(file_path):
            return False
        
        # التحقق من امتداد الملف
        audio_extensions = ['.mp3', '.m4a', '.wav', '.flac', '.ogg', '.webm']
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in audio_extensions:
            return False
        
        # التحقق من حجم الملف
        try:
            file_size = os.path.getsize(file_path)
            max_size = 100 * 1024 * 1024  # 100MB
            
            if file_size > max_size:
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def validate_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        التحقق من صحة البيانات الوصفية وتنظيفها
        
        Args:
            metadata: البيانات الوصفية
            
        Returns:
            البيانات الوصفية المنظفة
            
        Raises:
            ValidationError: في حالة وجود بيانات غير صحيحة
        """
        if not isinstance(metadata, dict):
            raise ValidationError("البيانات الوصفية يجب أن تكون قاموساً")
        
        cleaned_metadata = {}
        
        # تنظيف اسم الأغنية
        title = metadata.get('title', '').strip()
        if title:
            title = DataValidator._clean_text(title)
            if len(title) > 200:
                title = title[:200]
            cleaned_metadata['title'] = title
        
        # تنظيف اسم الفنان
        artist = metadata.get('artist', '').strip()
        if artist:
            artist = DataValidator._clean_text(artist)
            if len(artist) > 100:
                artist = artist[:100]
            cleaned_metadata['artist'] = artist
        
        # تنظيف اسم الألبوم
        album = metadata.get('album', '').strip()
        if album:
            album = DataValidator._clean_text(album)
            if len(album) > 200:
                album = album[:200]
            cleaned_metadata['album'] = album
        
        # التحقق من السنة
        year = metadata.get('year')
        if year:
            try:
                year = int(year)
                if 1900 <= year <= 2030:
                    cleaned_metadata['year'] = year
            except (ValueError, TypeError):
                pass
        
        # تنظيف النوع الموسيقي
        genre = metadata.get('genre', '').strip()
        if genre:
            genre = DataValidator._clean_text(genre)
            if len(genre) > 50:
                genre = genre[:50]
            cleaned_metadata['genre'] = genre
        
        return cleaned_metadata
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        تنظيف النص من الأحرف غير المرغوبة
        
        Args:
            text: النص المراد تنظيفه
            
        Returns:
            النص المنظف
        """
        if not text:
            return ""
        
        # إزالة الأحرف الخاصة الضارة
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text)
        
        # إزالة الأحرف غير المطبوعة
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        return text.strip()
    
    @staticmethod
    def is_valid_user_id(user_id: Any) -> bool:
        """
        التحقق من صحة معرف المستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            True إذا كان المعرف صحيحاً
        """
        try:
            user_id = int(user_id)
            return user_id > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_config() -> List[str]:
        """
        التحقق من صحة إعدادات التطبيق
        
        Returns:
            قائمة بالأخطاء المكتشفة
        """
        from config import Config
        
        errors = []
        
        # التحقق من توكن Telegram
        if not Config.TELEGRAM_BOT_TOKEN:
            errors.append("توكن Telegram Bot مفقود")
        elif not re.match(r'^\d+:[A-Za-z0-9_-]+$', Config.TELEGRAM_BOT_TOKEN):
            errors.append("تنسيق توكن Telegram Bot غير صحيح")
        
        # التحقق من مفتاح YouTube API
        if not Config.YOUTUBE_API_KEY:
            errors.append("مفتاح YouTube API مفقود")
        
        # التحقق من مفتاح OpenAI API
        if not Config.OPENAI_API_KEY:
            errors.append("مفتاح OpenAI API مفقود")
        
        # التحقق من مجلد الملفات المؤقتة
        if not os.path.exists(Config.TEMP_DIR):
            try:
                os.makedirs(Config.TEMP_DIR, exist_ok=True)
            except Exception as e:
                errors.append(f"لا يمكن إنشاء مجلد الملفات المؤقتة: {e}")
        
        # التحقق من إعدادات الصوت
        try:
            quality = int(Config.AUDIO_QUALITY)
            if quality < 64 or quality > 320:
                errors.append("جودة الصوت يجب أن تكون بين 64 و 320 kbps")
        except ValueError:
            errors.append("جودة الصوت يجب أن تكون رقماً")
        
        # التحقق من حد حجم الملف
        try:
            max_size = int(Config.MAX_FILE_SIZE)
            if max_size < 1 or max_size > 100:
                errors.append("حد حجم الملف يجب أن يكون بين 1 و 100 MB")
        except ValueError:
            errors.append("حد حجم الملف يجب أن يكون رقماً")
        
        return errors
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        تنظيف اسم الملف من الأحرف غير المسموحة
        
        Args:
            filename: اسم الملف
            
        Returns:
            اسم الملف المنظف
        """
        if not filename:
            return "untitled"
        
        # إزالة الأحرف غير المسموحة في أسماء الملفات
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # إزالة النقاط في البداية والنهاية
        sanitized = sanitized.strip('. ')
        
        # تحديد الطول الأقصى
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        # التأكد من عدم كون الاسم فارغاً
        if not sanitized:
            sanitized = "untitled"
        
        return sanitized
