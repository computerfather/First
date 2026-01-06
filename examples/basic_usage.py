#!/usr/bin/env python3
"""
مثال أساسي على استخدام مكونات البوت
Basic usage example of bot components
"""

import sys
import os
import asyncio
from pathlib import Path

# إضافة مجلد src إلى مسار Python
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.youtube.youtube_api import YouTubeAPI
from src.audio.downloader import AudioDownloader
from src.audio.audio_processor import AudioProcessor
from src.audio.metadata_tagger import MetadataTagger
from src.ai.ai_metadata import AIMetadataEnhancer
from src.utils.logger import setup_logger

# إعداد التسجيل
logger = setup_logger('BasicUsageExample')

async def example_youtube_search():
    """مثال على البحث في YouTube"""
    print("🔍 مثال البحث في YouTube")
    print("=" * 40)
    
    try:
        # تهيئة YouTube API (يتطلب مفتاح API صحيح)
        youtube = YouTubeAPI()
        
        # البحث عن أغنية
        query = "Fairuz - Li Beirut"
        print(f"البحث عن: {query}")
        
        videos = youtube.search_videos(query, max_results=3)
        
        if videos:
            print(f"تم العثور على {len(videos)} نتيجة:")
            for i, video in enumerate(videos, 1):
                print(f"{i}. {video['title']}")
                print(f"   القناة: {video['channel']}")
                print(f"   الرابط: {video['url']}")
                print()
        else:
            print("لم يتم العثور على نتائج")
            
    except Exception as e:
        print(f"خطأ في البحث: {e}")

def example_audio_download():
    """مثال على تحميل الصوت"""
    print("⬇️ مثال تحميل الصوت")
    print("=" * 40)
    
    try:
        # تهيئة محمل الصوت
        downloader = AudioDownloader()
        
        # رابط تجريبي (يجب استبداله برابط صحيح)
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"تحميل من: {video_url}")
        
        # تحميل الصوت
        download_info = downloader.download_audio(video_url)
        
        if download_info:
            print("تم التحميل بنجاح!")
            print(f"الملف: {download_info['filename']}")
            print(f"الحجم: {download_info['filesize']} بايت")
            print(f"المدة: {download_info['duration']} ثانية")
            
            # حذف الملف التجريبي
            if os.path.exists(download_info['filepath']):
                os.remove(download_info['filepath'])
                print("تم حذف الملف التجريبي")
        else:
            print("فشل في التحميل")
            
    except Exception as e:
        print(f"خطأ في التحميل: {e}")

def example_audio_processing():
    """مثال على معالجة الصوت"""
    print("⚙️ مثال معالجة الصوت")
    print("=" * 40)
    
    try:
        # تهيئة معالج الصوت
        processor = AudioProcessor()
        
        # إنشاء ملف صوتي تجريبي (في الواقع، ستستخدم ملف حقيقي)
        print("ملاحظة: هذا المثال يتطلب ملف صوتي حقيقي")
        print("يمكنك استخدام الدالة process_audio_complete() مع ملف MP3 موجود")
        
        # مثال على الاستخدام:
        # processed_file = processor.process_audio_complete(
        #     "input_file.mp3",
        #     normalize=True,
        #     trim_silence=True
        # )
        
        print("تم إعداد معالج الصوت بنجاح")
        
    except Exception as e:
        print(f"خطأ في معالجة الصوت: {e}")

def example_ai_metadata():
    """مثال على تحسين البيانات الوصفية بالذكاء الاصطناعي"""
    print("🤖 مثال تحسين البيانات الوصفية")
    print("=" * 40)
    
    try:
        # تهيئة محسن البيانات (يتطلب مفتاح OpenAI API صحيح)
        ai_enhancer = AIMetadataEnhancer()
        
        # عنوان فيديو تجريبي
        video_title = "Fairuz - Li Beirut [Official Audio] HD"
        channel_name = "Fairuz Official"
        
        print(f"العنوان الأصلي: {video_title}")
        print(f"القناة: {channel_name}")
        
        # تحسين البيانات
        enhanced = ai_enhancer.enhance_metadata(
            video_title, 
            channel_name
        )
        
        print("\nالبيانات المحسنة:")
        print(f"الفنان: {enhanced['artist']}")
        print(f"الأغنية: {enhanced['title']}")
        print(f"مستوى الثقة: {enhanced['confidence']}/10")
        
    except Exception as e:
        print(f"خطأ في تحسين البيانات: {e}")

def example_metadata_tagging():
    """مثال على إضافة البيانات الوصفية"""
    print("🏷️ مثال إضافة البيانات الوصفية")
    print("=" * 40)
    
    try:
        # تهيئة معالج البيانات الوصفية
        tagger = MetadataTagger()
        
        # بيانات وصفية تجريبية
        metadata = {
            'title': 'لي بيروت',
            'artist': 'فيروز',
            'album': 'أغاني فيروز',
            'year': 1975,
            'genre': 'Arabic Music'
        }
        
        print("البيانات الوصفية التجريبية:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        print("\nملاحظة: هذا المثال يتطلب ملف MP3 حقيقي")
        print("يمكنك استخدام الدالة add_metadata() مع ملف MP3 موجود")
        
        # مثال على الاستخدام:
        # success = tagger.add_metadata(
        #     "audio_file.mp3",
        #     metadata,
        #     cover_url="https://example.com/cover.jpg"
        # )
        
        print("تم إعداد معالج البيانات الوصفية بنجاح")
        
    except Exception as e:
        print(f"خطأ في معالجة البيانات الوصفية: {e}")

async def run_all_examples():
    """تشغيل جميع الأمثلة"""
    print("🎵 أمثلة استخدام بوت تحميل الموسيقى")
    print("=" * 50)
    print()
    
    # مثال البحث في YouTube
    await example_youtube_search()
    print()
    
    # مثال تحميل الصوت
    example_audio_download()
    print()
    
    # مثال معالجة الصوت
    example_audio_processing()
    print()
    
    # مثال تحسين البيانات بالذكاء الاصطناعي
    example_ai_metadata()
    print()
    
    # مثال إضافة البيانات الوصفية
    example_metadata_tagging()
    print()
    
    print("✅ انتهت جميع الأمثلة")

def main():
    """الدالة الرئيسية"""
    try:
        # تشغيل الأمثلة
        asyncio.run(run_all_examples())
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الأمثلة")
    except Exception as e:
        print(f"❌ خطأ في تشغيل الأمثلة: {e}")

if __name__ == "__main__":
    main()
