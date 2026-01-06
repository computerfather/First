"""
وحدة معالجة الصوت باستخدام FFmpeg
Audio processing module using FFmpeg
"""

import os
import logging
import subprocess
from typing import Optional, Dict, Any
from config import Config, FFMPEG_OPTIONS

logger = logging.getLogger(__name__)

class AudioProcessor:
    """فئة لمعالجة الصوت باستخدام FFmpeg"""
    
    def __init__(self, temp_dir: str = None):
        """
        تهيئة معالج الصوت
        
        Args:
            temp_dir: مجلد الملفات المؤقتة
        """
        self.temp_dir = temp_dir or Config.TEMP_DIR
        self._ensure_ffmpeg_available()
    
    def _ensure_ffmpeg_available(self):
        """التحقق من توفر FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("FFmpeg متوفر ويعمل بشكل صحيح")
            else:
                raise RuntimeError("FFmpeg غير متوفر أو لا يعمل بشكل صحيح")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"FFmpeg غير متوفر: {e}")
            raise RuntimeError("يجب تثبيت FFmpeg لتشغيل البوت")
    
    def convert_to_mp3(self, input_file: str, output_file: str = None, 
                      quality: str = None) -> Optional[str]:
        """
        تحويل ملف صوتي إلى MP3
        
        Args:
            input_file: مسار الملف المدخل
            output_file: مسار الملف المخرج (اختياري)
            quality: جودة الصوت (اختياري)
            
        Returns:
            مسار الملف المحول أو None في حالة الفشل
        """
        try:
            if not os.path.exists(input_file):
                logger.error(f"الملف المدخل غير موجود: {input_file}")
                return None
            
            # تحديد ملف الإخراج
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = os.path.join(self.temp_dir, f"{base_name}.mp3")
            
            # تحديد الجودة
            audio_quality = quality or Config.AUDIO_QUALITY
            
            # بناء أمر FFmpeg
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-vn',  # بدون فيديو
                '-acodec', 'libmp3lame',
                '-ab', f'{audio_quality}k',
                '-ar', '44100',  # Sample rate
                '-ac', '2',      # Stereo
                '-y',            # Overwrite output file
                output_file
            ]
            
            logger.info(f"تحويل الملف إلى MP3: {input_file} -> {output_file}")
            
            # تشغيل الأمر
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                if os.path.exists(output_file):
                    logger.info(f"تم التحويل بنجاح: {output_file}")
                    return output_file
                else:
                    logger.error("فشل في إنشاء الملف المحول")
                    return None
            else:
                logger.error(f"خطأ في FFmpeg: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("انتهت مهلة تحويل الملف")
            return None
        except Exception as e:
            logger.error(f"خطأ في تحويل الملف: {e}")
            return None
    
    def normalize_audio(self, input_file: str, output_file: str = None) -> Optional[str]:
        """
        تطبيع مستوى الصوت
        
        Args:
            input_file: مسار الملف المدخل
            output_file: مسار الملف المخرج (اختياري)
            
        Returns:
            مسار الملف المطبع أو None في حالة الفشل
        """
        try:
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = os.path.join(self.temp_dir, f"{base_name}_normalized.mp3")
            
            # أمر تطبيع الصوت
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                '-y',
                output_file
            ]
            
            logger.info(f"تطبيع مستوى الصوت: {input_file}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_file):
                logger.info(f"تم تطبيع الصوت بنجاح: {output_file}")
                return output_file
            else:
                logger.error(f"فشل في تطبيع الصوت: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في تطبيع الصوت: {e}")
            return None
    
    def trim_silence(self, input_file: str, output_file: str = None) -> Optional[str]:
        """
        إزالة الصمت من بداية ونهاية الملف
        
        Args:
            input_file: مسار الملف المدخل
            output_file: مسار الملف المخرج (اختياري)
            
        Returns:
            مسار الملف المقصوص أو None في حالة الفشل
        """
        try:
            if not output_file:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = os.path.join(self.temp_dir, f"{base_name}_trimmed.mp3")
            
            # أمر إزالة الصمت
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-af', 'silenceremove=start_periods=1:start_duration=1:start_threshold=-60dB:detection=peak,aformat=dblp,areverse,silenceremove=start_periods=1:start_duration=1:start_threshold=-60dB:detection=peak,aformat=dblp,areverse',
                '-y',
                output_file
            ]
            
            logger.info(f"إزالة الصمت من الملف: {input_file}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_file):
                logger.info(f"تم قص الصمت بنجاح: {output_file}")
                return output_file
            else:
                logger.warning(f"فشل في قص الصمت، استخدام الملف الأصلي: {result.stderr}")
                return input_file  # إرجاع الملف الأصلي في حالة الفشل
                
        except Exception as e:
            logger.error(f"خطأ في قص الصمت: {e}")
            return input_file  # إرجاع الملف الأصلي في حالة الفشل
    
    def get_audio_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        جلب معلومات الملف الصوتي
        
        Args:
            file_path: مسار الملف
            
        Returns:
            معلومات الملف الصوتي
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                # استخراج معلومات الصوت
                audio_stream = None
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break
                
                if audio_stream:
                    format_info = data.get('format', {})
                    return {
                        'duration': float(format_info.get('duration', 0)),
                        'bitrate': int(format_info.get('bit_rate', 0)),
                        'size': int(format_info.get('size', 0)),
                        'codec': audio_stream.get('codec_name'),
                        'sample_rate': int(audio_stream.get('sample_rate', 0)),
                        'channels': int(audio_stream.get('channels', 0)),
                        'channel_layout': audio_stream.get('channel_layout')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في جلب معلومات الملف: {e}")
            return None
    
    def process_audio_complete(self, input_file: str, 
                             normalize: bool = True, 
                             trim_silence: bool = True,
                             target_quality: str = None) -> Optional[str]:
        """
        معالجة شاملة للملف الصوتي
        
        Args:
            input_file: مسار الملف المدخل
            normalize: تطبيع مستوى الصوت
            trim_silence: إزالة الصمت
            target_quality: الجودة المطلوبة
            
        Returns:
            مسار الملف المعالج النهائي
        """
        try:
            current_file = input_file
            
            # 1. تحويل إلى MP3 إذا لم يكن كذلك
            if not current_file.lower().endswith('.mp3'):
                logger.info("تحويل الملف إلى MP3...")
                current_file = self.convert_to_mp3(current_file, quality=target_quality)
                if not current_file:
                    return None
            
            # 2. إزالة الصمت إذا طُلب ذلك
            if trim_silence:
                logger.info("إزالة الصمت...")
                trimmed_file = self.trim_silence(current_file)
                if trimmed_file and trimmed_file != current_file:
                    # حذف الملف المؤقت السابق
                    if current_file != input_file:
                        self._safe_remove(current_file)
                    current_file = trimmed_file
            
            # 3. تطبيع مستوى الصوت إذا طُلب ذلك
            if normalize:
                logger.info("تطبيع مستوى الصوت...")
                normalized_file = self.normalize_audio(current_file)
                if normalized_file and normalized_file != current_file:
                    # حذف الملف المؤقت السابق
                    if current_file != input_file:
                        self._safe_remove(current_file)
                    current_file = normalized_file
            
            logger.info(f"تمت معالجة الملف بنجاح: {current_file}")
            return current_file
            
        except Exception as e:
            logger.error(f"خطأ في المعالجة الشاملة: {e}")
            return None
    
    def _safe_remove(self, file_path: str):
        """حذف آمن للملف"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"تم حذف الملف المؤقت: {file_path}")
        except Exception as e:
            logger.warning(f"لم يتم حذف الملف المؤقت {file_path}: {e}")
    
    def cleanup_processed_files(self, keep_final: bool = True):
        """تنظيف الملفات المعالجة"""
        try:
            if not os.path.exists(self.temp_dir):
                return
            
            patterns_to_remove = ['_normalized', '_trimmed', '_temp'] if keep_final else []
            
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                
                if os.path.isfile(filepath):
                    # حذف الملفات المؤقتة
                    if any(pattern in filename for pattern in patterns_to_remove):
                        self._safe_remove(filepath)
                        
        except Exception as e:
            logger.error(f"خطأ في تنظيف الملفات المعالجة: {e}")
