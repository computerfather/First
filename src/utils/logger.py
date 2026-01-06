"""
نظام تسجيل الأحداث
Logging system configuration
"""

import logging
import logging.handlers
import os
from datetime import datetime
import colorlog
from config import Config

def setup_logger(name: str = None, level: str = None) -> logging.Logger:
    """
    إعداد نظام تسجيل الأحداث
    
    Args:
        name: اسم المسجل
        level: مستوى التسجيل
        
    Returns:
        مسجل الأحداث المُعد
    """
    logger_name = name or __name__
    log_level = level or Config.LOG_LEVEL
    
    # إنشاء المسجل
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # تجنب إضافة معالجات متعددة
    if logger.handlers:
        return logger
    
    # إنشاء مجلد السجلات
    log_dir = os.path.dirname(Config.LOG_FILE) if os.path.dirname(Config.LOG_FILE) else 'logs'
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # تنسيق الرسائل
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # تنسيق ملون للكونسول
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # معالج الكونسول
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # معالج الملف
    file_handler = logging.handlers.RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # معالج الأخطاء المنفصل
    error_log_file = Config.LOG_FILE.replace('.log', '_errors.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

def log_function_call(func):
    """
    ديكوريتر لتسجيل استدعاءات الدوال
    
    Args:
        func: الدالة المراد تسجيل استدعاءاتها
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"استدعاء الدالة: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"انتهاء الدالة: {func.__name__} بنجاح")
            return result
        except Exception as e:
            logger.error(f"خطأ في الدالة {func.__name__}: {e}")
            raise
    
    return wrapper

def log_execution_time(func):
    """
    ديكوريتر لتسجيل وقت تنفيذ الدوال
    
    Args:
        func: الدالة المراد قياس وقت تنفيذها
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"وقت تنفيذ {func.__name__}: {execution_time:.2f} ثانية")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"فشل {func.__name__} بعد {execution_time:.2f} ثانية: {e}")
            raise
    
    return wrapper

class BotLogger:
    """فئة مخصصة لتسجيل أحداث البوت"""
    
    def __init__(self, name: str = "TelegramMusicBot"):
        self.logger = setup_logger(name)
        self.stats = {
            'info_count': 0,
            'warning_count': 0,
            'error_count': 0,
            'start_time': datetime.now()
        }
    
    def info(self, message: str, user_id: int = None):
        """تسجيل رسالة معلوماتية"""
        if user_id:
            message = f"[المستخدم {user_id}] {message}"
        self.logger.info(message)
        self.stats['info_count'] += 1
    
    def warning(self, message: str, user_id: int = None):
        """تسجيل تحذير"""
        if user_id:
            message = f"[المستخدم {user_id}] {message}"
        self.logger.warning(message)
        self.stats['warning_count'] += 1
    
    def error(self, message: str, user_id: int = None, exception: Exception = None):
        """تسجيل خطأ"""
        if user_id:
            message = f"[المستخدم {user_id}] {message}"
        
        if exception:
            message = f"{message} - التفاصيل: {str(exception)}"
        
        self.logger.error(message)
        self.stats['error_count'] += 1
    
    def debug(self, message: str, user_id: int = None):
        """تسجيل رسالة تصحيح"""
        if user_id:
            message = f"[المستخدم {user_id}] {message}"
        self.logger.debug(message)
    
    def user_action(self, action: str, user_id: int, details: str = None):
        """تسجيل إجراء المستخدم"""
        message = f"إجراء المستخدم {user_id}: {action}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def download_started(self, user_id: int, query: str):
        """تسجيل بداية التحميل"""
        self.user_action("بدء التحميل", user_id, f"الطلب: {query}")
    
    def download_completed(self, user_id: int, title: str, duration: float = None):
        """تسجيل انتهاء التحميل"""
        details = f"الأغنية: {title}"
        if duration:
            details += f" - المدة: {duration:.2f}s"
        self.user_action("انتهاء التحميل", user_id, details)
    
    def download_failed(self, user_id: int, query: str, error: str):
        """تسجيل فشل التحميل"""
        self.error(f"فشل التحميل للمستخدم {user_id}: {query} - {error}")
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات السجلات"""
        runtime = datetime.now() - self.stats['start_time']
        return {
            **self.stats,
            'runtime_hours': runtime.total_seconds() / 3600,
            'runtime_str': str(runtime).split('.')[0]  # إزالة الميكروثواني
        }
    
    def reset_stats(self):
        """إعادة تعيين الإحصائيات"""
        self.stats = {
            'info_count': 0,
            'warning_count': 0,
            'error_count': 0,
            'start_time': datetime.now()
        }

# إنشاء مسجل عام للبوت
bot_logger = BotLogger()

def get_bot_logger() -> BotLogger:
    """الحصول على مسجل البوت العام"""
    return bot_logger
