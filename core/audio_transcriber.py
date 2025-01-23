import os
import sys
import requests
import math 
import wave
import json
import io
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment
from typing import Optional
from vosk import Model, KaldiRecognizer
from pathlib import Path
from loguru import logger
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv()

class AudioTranscriber:
    def __init__(self, audio_url: str, title: str='transcript', language: str='chinese', model: str='vosk'):
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        self.MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
        
        # Set basic attributes
        self.audio_url = audio_url
        self.title = title
        self.lang = language
        self.model = model
        
        # Create necessary directories
        self.static_path = project_root / "static"
        self.temp_dir = self.static_path / "temp"
        self.output_dir = self.static_path / "podcast_transcript"
        self.model_dir = self.static_path / "model"

        # Create all directories
        for directory in [self.temp_dir, self.model_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Set file paths
        self.temp_audio_path = self.temp_dir / "temp_audio.mp3"
        self.temp_chunk_path = self.temp_dir / "temp_chunk.mp3"
        self.temp_audio_wav_path = self.temp_dir / "temp_audio.wav"
        self.output_path = self.output_dir / f"{self.title}_{self.model}.txt"

    def _download_audio(self) -> bytes:
        """Download audio file from URL"""
        response = requests.get(self.audio_url)
        response.raise_for_status()
        return response.content

    def transcribe_with_openai(self) -> Optional[str]:
        """Transcribe audio using OpenAI's Whisper model"""
        try:
            audio_data = self._download_audio()
            if len(audio_data) <= self.MAX_FILE_SIZE:
                return self._transcribe_chunk(audio_data)
            return self._transcribe_large_file(audio_data)
        except Exception as e:
            print(f"OpenAI transcription error: {str(e)}")
            return None
        finally:
            self._cleanup_files()

    def _transcribe_chunk(self, audio_data: bytes) -> str:
        """Transcribe a single chunk of audio using OpenAI"""
        with open(self.temp_audio_path, "wb") as f:
            f.write(audio_data)
        with open(self.temp_audio_path, "rb") as audio_file:
            return self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

    def _transcribe_large_file(self, audio_data: bytes) -> str:
        """Handle large audio files by splitting into chunks"""
        audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
        chunk_length_ms = 10 * 60 * 1000  # 10 minutes
        chunks = math.ceil(len(audio) / chunk_length_ms)
        
        transcripts = []
        for i in range(chunks):
            chunk = audio[i*chunk_length_ms:min((i+1)*chunk_length_ms, len(audio))]
            chunk.export(str(self.temp_chunk_path), format="mp3")
            if self.temp_chunk_path.stat().st_size <= self.MAX_FILE_SIZE:
                with open(self.temp_chunk_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                transcripts.append(transcript)
            else:
                print(f"Warning: Chunk {i+1} exceeds size limit and was skipped")
        
        return "\n".join(transcripts)

    def transcribe_with_vosk(self) -> Optional[str]:
        """Transcribe audio using Vosk model"""
        try:
            wav_path = self._prepare_audio_for_vosk()
            if not wav_path:
                return None

            model_path = self._get_vosk_model_path()
            if not model_path:
                return None

            return self._process_with_vosk(wav_path, model_path)
        except Exception as e:
            print(f"Vosk transcription error: {str(e)}")
            return None
        finally:
            self._cleanup_files()

    def _prepare_audio_for_vosk(self) -> Optional[Path]:
        """Prepare audio file for Vosk processing"""
        try:
            audio_data = self._download_audio()
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(str(self.temp_audio_wav_path), format="wav")
            return self.temp_audio_wav_path
        except Exception as e:
            print(f"Error preparing audio: {e}")
            return None

    def _get_vosk_model_path(self) -> Optional[Path]:
        """Get path to Vosk model"""
        model_name = "vosk-model-small-en-us-0.22" if self.lang == "english" else "vosk-model-cn-0.22"
        model_path = self.model_dir / model_name
        
        if not model_path.exists():
            print(f"""
Please download and extract the Vosk model:
1. Visit https://alphacephei.com/vosk/models
2. Download {model_name}
3. Extract to {model_path}
            """)
            return None
        return model_path

    def _process_with_vosk(self, wav_path: Path, model_path: Path) -> str:
        """Process audio with Vosk model"""
        model = Model(str(model_path))
        wf = wave.open(str(wav_path), "rb")
        recognizer = KaldiRecognizer(model, wf.getframerate())
        
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                results.append(result.get('text', '').replace(" ", ""))
        
        results.append(json.loads(recognizer.FinalResult()).get('text', ''))
        return ' '.join(filter(None, results))

    def _cleanup_files(self):
        """Clean up temporary files"""
        for path in [self.temp_audio_path, self.temp_chunk_path, self.temp_audio_wav_path]:
            try:
                if path.exists():
                    path.unlink()
            except Exception as e:
                print(f"Error cleaning up {path}: {e}")

    def transcribe(self) -> Optional[str]:
        """Main transcription function that handles both OpenAI and Vosk models"""
        try:
            # Choose transcription method based on model
            if self.model == "openai":
                logger.info("Using OpenAI model")
                transcript = self.transcribe_with_openai()
            else:
                logger.info("Using Vosk model")
                transcript = self.transcribe_with_vosk()

            if not transcript:
                print("Transcription failed")
                return None

            # Save transcript to file
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"Transcript saved to {self.output_path}")
            return self.output_path

        except Exception as e:
            print(f"Error in transcription process: {e}")
            return None
        finally:
            self._cleanup_files()


if __name__ == "__main__":
    # example:
    audio_url = 'https://m.cdn.firstory.me/track/ckga7ibs77fgl0875bxwgl0y0/cm64hea5r000h01x97ibvef9d/https%3A%2F%2Fd3mww1g1pfq2pt.cloudfront.net%2FRecord%2Fckga7ibs77fgl0875bxwgl0y0%2Fcm64hea5r000i01x9dqnt3imx.mp3?v=1737343398176'
    title = "【本週提醒】凡事都不要心急，過年先穩住"
    
    try:
        transcriber = AudioTranscriber(
            audio_url=audio_url,
            title=title,
            language="chinese",
            model="vosk"
        )
        transcript = transcriber.transcribe()
        if transcript:
            print("Transcription completed successfully!")
    except Exception as e:
        print(f"Error: {e}")

    