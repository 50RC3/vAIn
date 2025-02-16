import speech_recognition as sr
from gtts import gTTS
import sounddevice as sd
import numpy as np
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer, WhisperProcessor, WhisperForConditionalGeneration
import logging

logger = logging.getLogger(__name__)

class VoiceProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.wav2vec = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
        self.tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
        
        # Add Whisper model for improved transcription
        self.whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-base")
        self.whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
        
    def listen(self, duration=5):
        """Record audio from microphone"""
        try:
            with sr.Microphone() as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=duration)
                return audio
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            raise

    def transcribe(self, audio):
        """Convert speech to text using multiple models for accuracy"""
        try:
            # Convert audio data to the correct format for Whisper
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.float32)
            # Normalize audio data
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Try Whisper first
            input_features = self.whisper_processor(
                audio_data, 
                sampling_rate=16000, 
                return_tensors="pt"
            ).input_features
            predicted_ids = self.whisper_model.generate(input_features)
            transcription = self.whisper_processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            confidence = 0.9
            
            # Fallback to existing methods if needed
            if not transcription:
                # Try Google's speech recognition first
                text = self.recognizer.recognize_google(audio)
                confidence = 0.8
                
                # Fallback to Wav2Vec2 if Google fails
                if not text:
                    audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                    input_values = self.tokenizer(audio_data, return_tensors="pt").input_values
                    logits = self.wav2vec(input_values).logits
                    predicted_ids = torch.argmax(logits, dim=-1)
                    text = self.tokenizer.batch_decode(predicted_ids)[0]
                    confidence = 0.6
                    
                return text, confidence
            
            return transcription, confidence
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    def synthesize(self, text, language='en'):
        """Convert text to speech"""
        try:
            tts = gTTS(text=text, lang=language)
            # Save to temporary file and read back
            import tempfile
            import os
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            try:
                tts.save(temp_file.name)
                with open(temp_file.name, 'rb') as f:
                    audio_data = f.read()
                return audio_data
            finally:
                os.unlink(temp_file.name)
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise

    def play_audio(self, audio_data):
        """Play synthesized speech"""
        try:
            import io
            import soundfile as sf
            
            # Convert MP3 to WAV using soundfile
            with io.BytesIO(audio_data) as audio_io:
                data, samplerate = sf.read(audio_io)
                sd.play(data, samplerate)
                sd.wait()
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            raise
