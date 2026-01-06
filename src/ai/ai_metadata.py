"""
وحدة الذكاء الاصطناعي لتحسين البيانات الوصفية
AI module for enhancing metadata using OpenAI GPT
"""

import json
import logging
import re
from typing import Dict, Optional, Tuple
import openai
from config import Config

logger = logging.getLogger(__name__)

class AIMetadataEnhancer:
    """فئة لتحسين البيانات الوصفية باستخدام الذكاء الاصطناعي"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        تهيئة محسن البيانات الوصفية
        
        Args:
            api_key: مفتاح OpenAI API
            model: نموذج GPT المستخدم
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("مفتاح OpenAI API مطلوب")
        
        # تهيئة OpenAI client
        openai.api_key = self.api_key
        
        # Cache للنتائج لتوفير التكاليف
        self._cache = {}
        
        logger.info(f"تم تهيئة AI Metadata Enhancer باستخدام نموذج: {self.model}")
    
    def enhance_metadata(self, title: str, channel: str = None, description: str = None) -> Dict[str, str]:
        """
        تحسين البيانات الوصفية للأغنية
        
        Args:
            title: عنوان الفيديو
            channel: اسم القناة (اختياري)
            description: وصف الفيديو (اختياري)
            
        Returns:
            قاموس يحتوي على البيانات المحسنة
        """
        try:
            # التحقق من الـ cache أولاً
            cache_key = self._generate_cache_key(title, channel)
            if cache_key in self._cache:
                logger.info("استخدام النتيجة من الـ cache")
                return self._cache[cache_key]
            
            # بناء النص للذكاء الاصطناعي
            prompt = self._build_prompt(title, channel, description)
            
            logger.info(f"تحسين البيانات الوصفية لـ: {title}")
            
            # استدعاء OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت خبير في الموسيقى ومتخصص في استخراج وتنظيم البيانات الوصفية للأغاني. مهمتك هي تحليل عناوين الفيديوهات واستخراج اسم الفنان واسم الأغنية بدقة."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # استخراج النتيجة
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            # تنظيف وتحسين النتيجة
            enhanced_result = self._clean_and_validate_result(result, title)
            
            # حفظ في الـ cache
            self._cache[cache_key] = enhanced_result
            
            logger.info(f"تم تحسين البيانات: {enhanced_result}")
            return enhanced_result
            
        except json.JSONDecodeError as e:
            logger.error(f"خطأ في تحليل JSON من OpenAI: {e}")
            return self._fallback_extraction(title, channel)
        except Exception as e:
            logger.error(f"خطأ في تحسين البيانات الوصفية: {e}")
            return self._fallback_extraction(title, channel)
    
    def _build_prompt(self, title: str, channel: str = None, description: str = None) -> str:
        """بناء النص المرسل للذكاء الاصطناعي"""
        prompt = f"""
استخرج اسم الفنان واسم الأغنية من عنوان الفيديو التالي:

العنوان: "{title}"
"""
        
        if channel:
            prompt += f"اسم القناة: "{channel}"\n"
        
        if description and len(description) > 0:
            # أخذ أول 200 حرف من الوصف
            short_desc = description[:200] + "..." if len(description) > 200 else description
            prompt += f"الوصف: "{short_desc}"\n"
        
        prompt += """
قم بإرجاع النتيجة بصيغة JSON فقط مع المفاتيح التالية:
{
    "artist": "اسم الفنان",
    "title": "اسم الأغنية",
    "confidence": "مستوى الثقة من 1-10"
}

ملاحظات مهمة:
- إزالة الكلمات مثل: [Official Video], (Official Audio), HD, 4K, etc.
- إزالة أسماء شركات الإنتاج
- إذا كان العنوان يحتوي على "-" فغالباً ما يكون الجزء الأول هو الفنان والثاني هو الأغنية
- إذا لم تتمكن من تحديد الفنان، ضع "Unknown Artist"
- إذا لم تتمكن من تحديد الأغنية، استخدم العنوان الأصلي منظفاً
- مستوى الثقة: 10 = متأكد جداً، 1 = غير متأكد
"""
        
        return prompt
    
    def _clean_and_validate_result(self, result: Dict, original_title: str) -> Dict[str, str]:
        """تنظيف وتحقق من صحة النتيجة"""
        try:
            artist = result.get('artist', '').strip()
            title = result.get('title', '').strip()
            confidence = int(result.get('confidence', 5))
            
            # تنظيف اسم الفنان
            if artist:
                artist = self._clean_text(artist)
                if artist.lower() in ['unknown', 'غير معروف', 'مجهول']:
                    artist = "Unknown Artist"
            else:
                artist = "Unknown Artist"
            
            # تنظيف اسم الأغنية
            if title:
                title = self._clean_text(title)
            else:
                title = self._clean_text(original_title)
            
            # التحقق من الجودة
            if confidence < 3:
                logger.warning(f"مستوى ثقة منخفض ({confidence}) في النتيجة")
            
            return {
                'artist': artist,
                'title': title,
                'confidence': str(confidence),
                'original_title': original_title
            }
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف النتيجة: {e}")
            return self._fallback_extraction(original_title)
    
    def _clean_text(self, text: str) -> str:
        """تنظيف النص من الكلمات والرموز غير المرغوبة"""
        if not text:
            return ""
        
        # إزالة الكلمات غير المرغوبة
        unwanted_patterns = [
            r'\[.*?\]',  # [Official Video]
            r'\(.*?\)',  # (Official Audio)
            r'official\s*(video|audio|music|mv)',
            r'(hd|4k|1080p|720p)',
            r'(lyrics?|كلمات)',
            r'(remix|ريمكس)',
            r'(cover|كوفر)',
            r'(live|لايف|مباشر)',
            r'(ft\.?|feat\.?|featuring)',
            r'(prod\.?|produced by)',
            r'(dir\.?|directed by)',
            r'©.*',
            r'®.*',
            r'™.*'
        ]
        
        cleaned = text
        for pattern in unwanted_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # تنظيف المسافات والرموز الزائدة
        cleaned = re.sub(r'\s+', ' ', cleaned)  # مسافات متعددة
        cleaned = re.sub(r'[_\-]{2,}', '-', cleaned)  # شرطات متعددة
        cleaned = cleaned.strip(' -_')
        
        return cleaned
    
    def _fallback_extraction(self, title: str, channel: str = None) -> Dict[str, str]:
        """استخراج احتياطي بدون ذكاء اصطناعي"""
        logger.info("استخدام الاستخراج الاحتياطي")
        
        # تنظيف العنوان
        cleaned_title = self._clean_text(title)
        
        # محاولة استخراج الفنان والأغنية من العنوان
        artist = "Unknown Artist"
        song_title = cleaned_title
        
        # البحث عن نمط "Artist - Song"
        if ' - ' in cleaned_title:
            parts = cleaned_title.split(' - ', 1)
            if len(parts) == 2:
                artist = parts[0].strip()
                song_title = parts[1].strip()
        elif channel and channel.lower() not in cleaned_title.lower():
            # استخدام اسم القناة كفنان إذا لم يكن موجوداً في العنوان
            artist = channel
        
        return {
            'artist': artist,
            'title': song_title,
            'confidence': '3',  # ثقة متوسطة للاستخراج الاحتياطي
            'original_title': title
        }
    
    def _generate_cache_key(self, title: str, channel: str = None) -> str:
        """إنشاء مفتاح للـ cache"""
        key_parts = [title.lower().strip()]
        if channel:
            key_parts.append(channel.lower().strip())
        return '|'.join(key_parts)
    
    def extract_genre_and_mood(self, title: str, artist: str = None) -> Dict[str, str]:
        """
        استخراج النوع الموسيقي والمزاج (اختياري)
        
        Args:
            title: اسم الأغنية
            artist: اسم الفنان
            
        Returns:
            قاموس يحتوي على النوع والمزاج
        """
        try:
            prompt = f"""
حلل الأغنية التالية واستخرج النوع الموسيقي والمزاج:

الأغنية: "{title}"
"""
            if artist and artist != "Unknown Artist":
                prompt += f"الفنان: "{artist}"\n"
            
            prompt += """
أرجع النتيجة بصيغة JSON:
{
    "genre": "النوع الموسيقي (مثل: pop, rock, arabic, classical)",
    "mood": "المزاج (مثل: happy, sad, energetic, calm)"
}
"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "أنت خبير في تصنيف الموسيقى وتحديد الأنواع الموسيقية والمزاج."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return {
                'genre': result.get('genre', 'Unknown'),
                'mood': result.get('mood', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"خطأ في استخراج النوع والمزاج: {e}")
            return {'genre': 'Unknown', 'mood': 'Unknown'}
    
    def clear_cache(self):
        """مسح الـ cache"""
        self._cache.clear()
        logger.info("تم مسح cache البيانات الوصفية")
    
    def get_cache_size(self) -> int:
        """الحصول على حجم الـ cache"""
        return len(self._cache)
