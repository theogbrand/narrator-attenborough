import os
import requests
import wave
import struct
import numpy as np
from pygame import mixer
from dotenv import load_dotenv
import pygame
from time import time
import asyncio


load_dotenv()

def get_audio_response(text):
    url = "https://api.cartesia.ai/tts/bytes"
    payload = {
        "model_id": "sonic-english",
        # "model_id": "sonic-multilingual",
        "transcript": text,
        "duration": 123,
        "voice": {
            "mode": "id",
            # Jarvis model id
            "id": "1d92e61c-e8a2-4544-9d17-b6dfb38e212a"
        },
        "output_format": {
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": 44100
        }
    }
    headers = {
        "X-API-Key": os.environ["CARTESIA_API_KEY"],
        "Cartesia-Version": "2024-06-10",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the raw bytes to numpy array of float32
        audio_data = np.frombuffer(response.content, dtype=np.float32)
        
        # Normalize the float32 data to int16 range
        audio_data_int16 = (audio_data * 32767).astype(np.int16)
        
        # Open a new .wav file in write mode
        with wave.open('audio/response.wav', 'wb') as wav_file:
            # Set the parameters for the .wav file
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 2 bytes per sample for 16-bit audio
            wav_file.setframerate(payload['output_format']['sample_rate'])
            
            # Write the audio data
            wav_file.writeframes(audio_data_int16.tobytes())

        print("Audio saved as response.wav")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    return

# get_audio_response("Hello, brandon.") 
if __name__ == "__main__":
    while True:
        mixer.init()
        current_time = time()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("Speaking...")
        sound = mixer.Sound("audio/response.wav")
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))