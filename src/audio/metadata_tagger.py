"""
وحدة دمج البيانات الوصفية باستخدام Mutagen
Metadata tagging module using Mutagen
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from PIL import Image
import io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC, TPE2, TRCK
from mutagen.id3._util import ID3NoHeaderError

logger = logging.getLogger(__name__)

class MetadataTagger:
    """فئة لإضافة البيانات الوصفية لملفات MP3"""
    
    def __init__(self):
        """تهيئة معالج البيانات الوصفية"""
        logger.info("تم تهيئة MetadataTagger")
    
    def add_metadata(self, file_path: str, metadata: Dict[str, Any], 
                    cover_url: str = None) -> bool:
        """
        إضافة البيانات الوصفية لملف MP3
        
        Args:
            file_path: مسار الملف
            metadata: البيانات الوصفية
            cover_url: رابط صورة الغلاف (اختياري)
            
        Returns:
            True إذا تمت الإضافة بنجاح، False في حالة الفشل
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"الملف غير موجود: {file_path}")
                return False
            
            logger.info(f"إضافة البيانات الوصفية لـ: {file_path}")
            
            # تحميل الملف
            try:
                audio = MP3(file_path, ID3=ID3)
            except ID3NoHeaderError:
                # إنشاء header جديد إذا لم يكن موجوداً
                audio = MP3(file_path)
                audio.add_tags()
            
            # إضافة البيانات الأساسية
            self._add_basic_tags(audio, metadata)
            
            # إضافة صورة الغلاف
            if cover_url:
                self._add_cover_art(audio, cover_url)
            
            # حفظ التغييرات
            audio.save()
            
            logger.info("تم حفظ البيانات الوصفية بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إضافة البيانات الوصفية: {e}")
            return False
    
    def _add_basic_tags(self, audio: MP3, metadata: Dict[str, Any]):
        """إضافة البيانات الأساسية"""
        try:
            # اسم الأغنية
            if metadata.get('title'):
                audio.tags.add(TIT2(encoding=3, text=metadata['title']))
            
            # اسم الفنان
            if metadata.get('artist'):
                audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
                # إضافة الفنان كـ Album Artist أيضاً
                audio.tags.add(TPE2(encoding=3, text=metadata['artist']))
            
            # اسم الألبوم (استخدام اسم الأغنية إذا لم يكن متوفراً)
            album = metadata.get('album', metadata.get('title', 'Unknown Album'))
            audio.tags.add(TALB(encoding=3, text=album))
            
            # سنة الإصدار
            if metadata.get('year'):
                audio.tags.add(TDRC(encoding=3, text=str(metadata['year'])))
            elif metadata.get('upload_date'):
                # استخراج السنة من تاريخ الرفع
                try:
                    year = metadata['upload_date'][:4]
                    audio.tags.add(TDRC(encoding=3, text=year))
                except:
                    pass
            
            # النوع الموسيقي
            if metadata.get('genre'):
                audio.tags.add(TCON(encoding=3, text=metadata['genre']))
            
            # رقم المسار
            if metadata.get('track_number'):
                audio.tags.add(TRCK(encoding=3, text=str(metadata['track_number'])))
            
            logger.debug("تم إضافة البيانات الأساسية")
            
        except Exception as e:
            logger.error(f"خطأ في إضافة البيانات الأساسية: {e}")
    
    def _add_cover_art(self, audio: MP3, cover_url: str):
        """إضافة صورة الغلاف"""
        try:
            logger.info(f"تحميل صورة الغلاف من: {cover_url}")
            
            # تحميل الصورة
            response = requests.get(cover_url, timeout=30)
            response.raise_for_status()
            
            # التحقق من نوع الملف
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type:
                logger.warning(f"نوع الملف غير مدعوم: {content_type}")
                return
            
            # معالجة الصورة
            image_data = self._process_cover_image(response.content)
            
            if image_data:
                # إضافة الصورة للملف
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=image_data
                    )
                )
                logger.info("تم إضافة صورة الغلاف بنجاح")
            
        except requests.RequestException as e:
            logger.error(f"خطأ في تحميل صورة الغلاف: {e}")
        except Exception as e:
            logger.error(f"خطأ في معالجة صورة الغلاف: {e}")
    
    def _process_cover_image(self, image_data: bytes) -> Optional[bytes]:
        """معالجة وتحسين صورة الغلاف"""
        try:
            # فتح الصورة
            image = Image.open(io.BytesIO(image_data))
            
            # تحويل إلى RGB إذا لزم الأمر
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # تغيير الحجم إذا كانت كبيرة جداً
            max_size = (800, 800)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"تم تغيير حجم الصورة إلى: {image.size}")
            
            # حفظ كـ JPEG
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            processed_data = output.getvalue()
            
            # التحقق من الحجم النهائي
            if len(processed_data) > 1024 * 1024:  # أكبر من 1MB
                # ضغط أكثر
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=70, optimize=True)
                processed_data = output.getvalue()
            
            logger.debug(f"حجم صورة الغلاف النهائي: {len(processed_data)} بايت")
            return processed_data
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الصورة: {e}")
            return None
    
    def get_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        قراءة البيانات الوصفية من ملف MP3
        
        Args:
            file_path: مسار الملف
            
        Returns:
            البيانات الوصفية أو None
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"الملف غير موجود: {file_path}")
                return None
            
            audio = MP3(file_path, ID3=ID3)
            
            if not audio.tags:
                logger.warning("لا توجد بيانات وصفية في الملف")
                return None
            
            metadata = {}
            
            # استخراج البيانات الأساسية
            if audio.tags.get('TIT2'):
                metadata['title'] = str(audio.tags['TIT2'])
            
            if audio.tags.get('TPE1'):
                metadata['artist'] = str(audio.tags['TPE1'])
            
            if audio.tags.get('TALB'):
                metadata['album'] = str(audio.tags['TALB'])
            
            if audio.tags.get('TDRC'):
                metadata['year'] = str(audio.tags['TDRC'])
            
            if audio.tags.get('TCON'):
                metadata['genre'] = str(audio.tags['TCON'])
            
            if audio.tags.get('TRCK'):
                metadata['track_number'] = str(audio.tags['TRCK'])
            
            # معلومات الملف
            metadata['duration'] = audio.info.length
            metadata['bitrate'] = audio.info.bitrate
            metadata['sample_rate'] = audio.info.sample_rate
            
            # التحقق من وجود صورة الغلاف
            if audio.tags.get('APIC:Cover'):
                metadata['has_cover'] = True
            
            return metadata
            
        except Exception as e:
            logger.error(f"خطأ في قراءة البيانات الوصفية: {e}")
            return None
    
    def remove_metadata(self, file_path: str) -> bool:
        """
        إزالة جميع البيانات الوصفية من الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            True إذا تمت الإزالة بنجاح
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"الملف غير موجود: {file_path}")
                return False
            
            audio = MP3(file_path, ID3=ID3)
            
            if audio.tags:
                audio.tags.delete()
                audio.save()
                logger.info("تم حذف البيانات الوصفية")
                return True
            else:
                logger.info("لا توجد بيانات وصفية للحذف")
                return True
                
        except Exception as e:
            logger.error(f"خطأ في حذف البيانات الوصفية: {e}")
            return False
    
    def update_metadata(self, file_path: str, updates: Dict[str, Any]) -> bool:
        """
        تحديث البيانات الوصفية الموجودة
        
        Args:
            file_path: مسار الملف
            updates: البيانات المراد تحديثها
            
        Returns:
            True إذا تم التحديث بنجاح
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"الملف غير موجود: {file_path}")
                return False
            
            audio = MP3(file_path, ID3=ID3)
            
            if not audio.tags:
                audio.add_tags()
            
            # تحديث البيانات المحددة فقط
            if 'title' in updates:
                audio.tags.add(TIT2(encoding=3, text=updates['title']))
            
            if 'artist' in updates:
                audio.tags.add(TPE1(encoding=3, text=updates['artist']))
                audio.tags.add(TPE2(encoding=3, text=updates['artist']))
            
            if 'album' in updates:
                audio.tags.add(TALB(encoding=3, text=updates['album']))
            
            if 'year' in updates:
                audio.tags.add(TDRC(encoding=3, text=str(updates['year'])))
            
            if 'genre' in updates:
                audio.tags.add(TCON(encoding=3, text=updates['genre']))
            
            # حفظ التغييرات
            audio.save()
            
            logger.info("تم تحديث البيانات الوصفية بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث البيانات الوصفية: {e}")
            return False
    
    def extract_cover_art(self, file_path: str, output_path: str = None) -> Optional[str]:
        """
        استخراج صورة الغلاف من الملف
        
        Args:
            file_path: مسار الملف
            output_path: مسار حفظ الصورة (اختياري)
            
        Returns:
            مسار الصورة المستخرجة أو None
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"الملف غير موجود: {file_path}")
                return None
            
            audio = MP3(file_path, ID3=ID3)
            
            if not audio.tags or not audio.tags.get('APIC:Cover'):
                logger.warning("لا توجد صورة غلاف في الملف")
                return None
            
            cover_data = audio.tags['APIC:Cover'].data
            
            if not output_path:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = f"{base_name}_cover.jpg"
            
            with open(output_path, 'wb') as f:
                f.write(cover_data)
            
            logger.info(f"تم استخراج صورة الغلاف: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"خطأ في استخراج صورة الغلاف: {e}")
            return None
