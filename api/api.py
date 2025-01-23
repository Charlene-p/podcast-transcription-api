import sys
from pathlib import Path
from typing import Optional
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.podcast_feed_parser import PodcastFeedParser
from core.audio_transcriber import AudioTranscriber
from structure.basic import LanguageEnum, ModelEnum

def get_newest_episode(rss_url: str):
    parser = PodcastFeedParser(rss_url)
    episode = parser.get_newest_episode()
    if not episode:
        print("Failed to get episode")
    
    
    print(f"Processing episode: {episode.title}")
    print(f"Published: {episode.published_date}")
    print(f"Duration: {episode.duration_minutes} minutes")
    return episode

def transcribe_episode(audio_url: str, title: str, language: LanguageEnum = LanguageEnum.chinese, model: ModelEnum = ModelEnum.vosk):
    model = model.value
    language = language.value
    transcriber = AudioTranscriber(audio_url=audio_url, title=title, language=language, model=model)
    transcript = transcriber.transcribe()
    return transcript


if __name__ == "__main__":
    url = "https://feed.firstory.me/rss/user/ckga7ibs77fgl0875bxwgl0y0"
    get_newest_episode(url)
