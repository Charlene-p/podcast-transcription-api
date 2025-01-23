import feedparser
import ssl
import time
from datetime import datetime
from typing import Optional
import io


class PodcastEpisode:
    def __init__(self, title: str, published_date: str, duration_minutes: float, audio_url: str):
        self.title = title
        self.published_date = published_date
        self.duration_minutes = duration_minutes
        self.audio_url = audio_url

class PodcastFeedParser:
    def __init__(self, rss_url: str):
        self.rss_url = rss_url
        self._setup_ssl()

    def _setup_ssl(self):
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

    def get_newest_episode(self) -> Optional[PodcastEpisode]:
        feed = feedparser.parse(self.rss_url)
        
        if not feed.entries:
            print("No entries found in the feed")
            return None
        
        newest_episode = feed.entries[0]
        
        # Get publication time
        pub_time = newest_episode.get('published_parsed') or \
                   newest_episode.get('updated_parsed') or \
                   newest_episode.get('created_parsed')
        
        formatted_date = self._format_date(pub_time)
        duration_minutes = self._parse_duration(newest_episode.get('itunes_duration'))
        
        return PodcastEpisode(
            title=newest_episode.title,
            published_date=formatted_date,
            duration_minutes=duration_minutes,
            audio_url=newest_episode.enclosures[0].href
        )

    def _format_date(self, pub_time) -> str:
        if pub_time:
            pub_datetime = datetime.fromtimestamp(time.mktime(pub_time))
            return pub_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return "Publication date not available"

    def _parse_duration(self, duration: str) -> Optional[float]:
        if not duration or duration == 'Duration not available':
            return None
        
        try:
            if ':' in duration:
                parts = duration.split(':')
                if len(parts) == 3:  # HH:MM:SS
                    return round(int(parts[0]) * 60 + int(parts[1]) + int(parts[2])/60, 2)
                elif len(parts) == 2:  # MM:SS
                    return round(int(parts[0]) + int(parts[1])/60, 2)
            return round(float(duration) / 60, 2)
        except (ValueError, TypeError):
            return None
        
if __name__ == "__main__":
    rss_url = 'https://feed.firstory.me/rss/user/ckga7ibs77fgl0875bxwgl0y0'
    parser = PodcastFeedParser(rss_url)
    episode = parser.get_newest_episode()
    if not episode:
        print("Failed to get episode")
    
    print(f"Processing episode: {episode.title}")
    print(f"Published: {episode.published_date}")
    print(f"Duration: {episode.duration_minutes} minutes")