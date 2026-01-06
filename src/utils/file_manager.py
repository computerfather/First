"""
مدير الملفات والمجلدات المؤقتة
File and temporary directory manager
"""

import os
import shutil
import tempfile
import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import threading
import time
from config import Config

logger = logging.getLogger(__name__)

class FileManager:
    """فئة إدارة الملفات والمجلدات المؤقتة"""
    
    def __init__(self, temp_dir: str = None, auto_cleanup: bool = True):
        """
        تهيئة مدير الملفات
        
        Args:
            temp_dir: مجلد الملفات المؤقتة
            auto_cleanup: تفعيل التنظيف التلقائي
        """
        self.temp_dir = temp_dir or Config.TEMP_DIR
        self.auto_cleanup = auto_cleanup
        self.cleanup_interval = 3600  # ساعة واحدة
        self.max_file_age = 7200  # ساعتان
        
        # إنشاء المجلد إذا لم يكن موجوداً
        self._ensure_temp_dir()
        
        # بدء التنظيف التلقائي
        if self.auto_cleanup:
            self._start_auto_cleanup()
        
        logger.info(f"تم تهيئة مدير الملفات: {self.temp_dir}")
    
    def _ensure_temp_dir(self):
        """التأكد من وجود مجلد الملفات المؤقتة"""
        try:
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir, exist_ok=True)
                logger.info(f"تم إنشاء مجلد الملفات المؤقتة: {self.temp_dir}")
        except Exception as e:
            logger.error(f"خطأ في إنشاء مجلد الملفات المؤقتة: {e}")
            raise
    
    def _start_auto_cleanup(self):
        """بدء التنظيف التلقائي في خيط منفصل"""
        def cleanup_worker():
            while True:
                try:
                    self.cleanup_old_files()
                    time.sleep(self.cleanup_interval)
                except Exception as e:
                    logger.error(f"خطأ في التنظيف التلقائي: {e}")
                    time.sleep(60)  # انتظار دقيقة في حالة الخطأ
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("تم بدء التنظيف التلقائي")
    
    def create_temp_file(self, suffix: str = '', prefix: str = 'temp_') -> str:
        """
        إنشاء ملف مؤقت
        
        Args:
            suffix: لاحقة الملف
            prefix: بادئة الملف
            
        Returns:
            مسار الملف المؤقت
        """
        try:
            fd, temp_path = tempfile.mkstemp(
                suffix=suffix,
                prefix=prefix,
                dir=self.temp_dir
            )
            os.close(fd)  # إغلاق file descriptor
            
            logger.debug(f"تم إنشاء ملف مؤقت: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء ملف مؤقت: {e}")
            raise
    
    def create_temp_dir(self, prefix: str = 'temp_dir_') -> str:
        """
        إنشاء مجلد مؤقت
        
        Args:
            prefix: بادئة المجلد
            
        Returns:
            مسار المجلد المؤقت
        """
        try:
            temp_path = tempfile.mkdtemp(
                prefix=prefix,
                dir=self.temp_dir
            )
            
            logger.debug(f"تم إنشاء مجلد مؤقت: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء مجلد مؤقت: {e}")
            raise
    
    def safe_remove(self, path: str) -> bool:
        """
        حذف آمن للملف أو المجلد
        
        Args:
            path: مسار الملف أو المجلد
            
        Returns:
            True إذا تم الحذف بنجاح
        """
        try:
            if not os.path.exists(path):
                return True
            
            if os.path.isfile(path):
                os.remove(path)
                logger.debug(f"تم حذف الملف: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                logger.debug(f"تم حذف المجلد: {path}")
            
            return True
            
        except Exception as e:
            logger.warning(f"لم يتم حذف {path}: {e}")
            return False
    
    def move_file(self, src: str, dst: str) -> bool:
        """
        نقل ملف من مكان لآخر
        
        Args:
            src: المسار المصدر
            dst: المسار الهدف
            
        Returns:
            True إذا تم النقل بنجاح
        """
        try:
            # إنشاء مجلد الهدف إذا لم يكن موجوداً
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            
            shutil.move(src, dst)
            logger.debug(f"تم نقل الملف من {src} إلى {dst}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في نقل الملف من {src} إلى {dst}: {e}")
            return False
    
    def copy_file(self, src: str, dst: str) -> bool:
        """
        نسخ ملف
        
        Args:
            src: المسار المصدر
            dst: المسار الهدف
            
        Returns:
            True إذا تم النسخ بنجاح
        """
        try:
            # إنشاء مجلد الهدف إذا لم يكن موجوداً
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            
            shutil.copy2(src, dst)
            logger.debug(f"تم نسخ الملف من {src} إلى {dst}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في نسخ الملف من {src} إلى {dst}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """
        الحصول على معلومات الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            معلومات الملف أو None
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'accessed': datetime.fromtimestamp(stat.st_atime),
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path),
                'extension': os.path.splitext(file_path)[1].lower()
            }
            
        except Exception as e:
            logger.error(f"خطأ في جلب معلومات الملف {file_path}: {e}")
            return None
    
    def list_temp_files(self, pattern: str = None) -> List[Dict]:
        """
        عرض قائمة الملفات المؤقتة
        
        Args:
            pattern: نمط البحث (اختياري)
            
        Returns:
            قائمة بمعلومات الملفات
        """
        try:
            files = []
            
            if not os.path.exists(self.temp_dir):
                return files
            
            for item in os.listdir(self.temp_dir):
                item_path = os.path.join(self.temp_dir, item)
                
                # تطبيق النمط إذا تم تحديده
                if pattern and pattern not in item:
                    continue
                
                file_info = self.get_file_info(item_path)
                if file_info:
                    files.append(file_info)
            
            # ترتيب حسب تاريخ الإنشاء
            files.sort(key=lambda x: x['created'], reverse=True)
            
            return files
            
        except Exception as e:
            logger.error(f"خطأ في عرض الملفات المؤقتة: {e}")
            return []
    
    def cleanup_old_files(self, max_age_seconds: int = None) -> int:
        """
        تنظيف الملفات القديمة
        
        Args:
            max_age_seconds: العمر الأقصى للملفات بالثواني
            
        Returns:
            عدد الملفات المحذوفة
        """
        max_age = max_age_seconds or self.max_file_age
        cutoff_time = datetime.now() - timedelta(seconds=max_age)
        
        deleted_count = 0
        total_size_freed = 0
        
        try:
            files = self.list_temp_files()
            
            for file_info in files:
                if file_info['created'] < cutoff_time:
                    if self.safe_remove(file_info['path']):
                        deleted_count += 1
                        total_size_freed += file_info['size']
            
            if deleted_count > 0:
                size_mb = round(total_size_freed / (1024 * 1024), 2)
                logger.info(f"تم حذف {deleted_count} ملف قديم، تم توفير {size_mb} MB")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف الملفات القديمة: {e}")
            return 0
    
    def cleanup_all_temp_files(self) -> int:
        """
        حذف جميع الملفات المؤقتة
        
        Returns:
            عدد الملفات المحذوفة
        """
        deleted_count = 0
        
        try:
            files = self.list_temp_files()
            
            for file_info in files:
                if self.safe_remove(file_info['path']):
                    deleted_count += 1
            
            logger.info(f"تم حذف جميع الملفات المؤقتة: {deleted_count} ملف")
            return deleted_count
            
        except Exception as e:
            logger.error(f"خطأ في حذف جميع الملفات المؤقتة: {e}")
            return 0
    
    def get_temp_dir_stats(self) -> Dict:
        """
        الحصول على إحصائيات مجلد الملفات المؤقتة
        
        Returns:
            إحصائيات المجلد
        """
        try:
            files = self.list_temp_files()
            
            total_files = len(files)
            total_size = sum(f['size'] for f in files)
            total_size_mb = round(total_size / (1024 * 1024), 2)
            
            # تصنيف الملفات حسب النوع
            file_types = {}
            for file_info in files:
                ext = file_info['extension'] or 'no_extension'
                file_types[ext] = file_types.get(ext, 0) + 1
            
            # العثور على أقدم وأحدث ملف
            oldest_file = min(files, key=lambda x: x['created']) if files else None
            newest_file = max(files, key=lambda x: x['created']) if files else None
            
            return {
                'temp_dir': self.temp_dir,
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size_mb,
                'file_types': file_types,
                'oldest_file': oldest_file['name'] if oldest_file else None,
                'oldest_file_age': (datetime.now() - oldest_file['created']).total_seconds() if oldest_file else 0,
                'newest_file': newest_file['name'] if newest_file else None,
                'auto_cleanup_enabled': self.auto_cleanup,
                'cleanup_interval_seconds': self.cleanup_interval,
                'max_file_age_seconds': self.max_file_age
            }
            
        except Exception as e:
            logger.error(f"خطأ في جلب إحصائيات المجلد المؤقت: {e}")
            return {}
    
    def set_cleanup_settings(self, interval: int = None, max_age: int = None):
        """
        تعديل إعدادات التنظيف التلقائي
        
        Args:
            interval: فترة التنظيف بالثواني
            max_age: العمر الأقصى للملفات بالثواني
        """
        if interval is not None:
            self.cleanup_interval = interval
            logger.info(f"تم تعديل فترة التنظيف إلى: {interval} ثانية")
        
        if max_age is not None:
            self.max_file_age = max_age
            logger.info(f"تم تعديل العمر الأقصى للملفات إلى: {max_age} ثانية")

# إنشاء مدير ملفات عام
file_manager = FileManager()

def get_file_manager() -> FileManager:
    """الحصول على مدير الملفات العام"""
    return file_manager
