"""
وحدة YouTube API للبحث وجلب البيانات
YouTube API module for searching and fetching video data
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config

logger = logging.getLogger(__name__)

class YouTubeAPI:
    """فئة للتعامل مع YouTube API"""
    
    def __init__(self, api_key: str = None):
        """
        تهيئة YouTube API
        
        Args:
            api_key: مفتاح YouTube API
        """
        self.api_key = api_key or Config.YOUTUBE_API_KEY
        if not self.api_key:
            raise ValueError("مفتاح YouTube API مطلوب")
        
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            logger.info("تم تهيئة YouTube API بنجاح")
        except Exception as e:
            logger.error(f"فشل في تهيئة YouTube API: {e}")
            raise
    
    def search_videos(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        البحث عن الفيديوهات في YouTube
        
        Args:
            query: نص البحث
            max_results: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالفيديوهات المطابقة
        """
        try:
            logger.info(f"البحث عن: {query}")
            
            # تحسين استعلام البحث
            enhanced_query = self._enhance_search_query(query)
            
            search_response = self.youtube.search().list(
                q=enhanced_query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                videoCategoryId='10',  # Music category
                order='relevance'
            ).execute()
            
            videos = []
            for item in search_response['items']:
                video_info = self._extract_video_info(item)
                if video_info:
                    videos.append(video_info)
            
            logger.info(f"تم العثور على {len(videos)} فيديو")
            return videos
            
        except HttpError as e:
            logger.error(f"خطأ في YouTube API: {e}")
            return []
        except Exception as e:
            logger.error(f"خطأ في البحث: {e}")
            return []
    
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        جلب معلومات فيديو محدد
        
        Args:
            video_url: رابط الفيديو
            
        Returns:
            معلومات الفيديو أو None
        """
        try:
            video_id = self._extract_video_id(video_url)
            if not video_id:
                logger.error("لم يتم العثور على معرف الفيديو")
                return None
            
            video_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                logger.error("لم يتم العثور على الفيديو")
                return None
            
            video_data = video_response['items'][0]
            return self._extract_detailed_video_info(video_data)
            
        except Exception as e:
            logger.error(f"خطأ في جلب معلومات الفيديو: {e}")
            return None
    
    def _enhance_search_query(self, query: str) -> str:
        """تحسين استعلام البحث"""
        # إضافة كلمات مفتاحية للموسيقى
        music_keywords = ['music', 'song', 'audio', 'official']
        
        # إزالة الكلمات غير المرغوبة
        unwanted = ['video', 'clip', 'live', 'concert', 'cover']
        
        enhanced = query.lower()
        
        # إضافة كلمة music إذا لم تكن موجودة
        if not any(keyword in enhanced for keyword in music_keywords):
            enhanced += ' music'
        
        return enhanced
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """استخراج معرف الفيديو من الرابط"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_video_info(self, item: Dict) -> Optional[Dict]:
        """استخراج معلومات الفيديو من نتيجة البحث"""
        try:
            snippet = item['snippet']
            video_id = item['id']['videoId']
            
            # تصفية الفيديوهات غير الموسيقية
            title = snippet['title'].lower()
            if any(word in title for word in ['trailer', 'movie', 'news', 'interview']):
                return None
            
            return {
                'video_id': video_id,
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'description': snippet.get('description', ''),
                'thumbnail': snippet['thumbnails']['high']['url'],
                'published_at': snippet['publishedAt'],
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }
            
        except KeyError as e:
            logger.error(f"خطأ في استخراج معلومات الفيديو: {e}")
            return None
    
    def _extract_detailed_video_info(self, video_data: Dict) -> Dict:
        """استخراج معلومات مفصلة للفيديو"""
        snippet = video_data['snippet']
        content_details = video_data['contentDetails']
        statistics = video_data.get('statistics', {})
        
        # تحويل مدة الفيديو من ISO 8601 إلى ثواني
        duration = self._parse_duration(content_details['duration'])
        
        return {
            'video_id': video_data['id'],
            'title': snippet['title'],
            'channel': snippet['channelTitle'],
            'description': snippet.get('description', ''),
            'thumbnail': snippet['thumbnails']['high']['url'],
            'duration': duration,
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'published_at': snippet['publishedAt'],
            'url': f'https://www.youtube.com/watch?v={video_data["id"]}'
        }
    
    def _parse_duration(self, duration_str: str) -> int:
        """تحويل مدة ISO 8601 إلى ثواني"""
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def is_valid_youtube_url(self, url: str) -> bool:
        """التحقق من صحة رابط YouTube"""
        return self._extract_video_id(url) is not None
    
    def get_best_match(self, query: str) -> Optional[Dict]:
        """الحصول على أفضل نتيجة مطابقة"""
        videos = self.search_videos(query, max_results=1)
        return videos[0] if videos else None
