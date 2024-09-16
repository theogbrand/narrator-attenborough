import os
import requests
import wave
import struct
import numpy as np
from pygame import mixer
from dotenv import load_dotenv
import pygame
from time import time
import pyaudio
from cartesia import Cartesia


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
            "id": "1d92e61c-e8a2-4544-9d17-b6dfb38e212a",
        },
        "output_format": {
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": 44100,
        },
    }
    headers = {
        "X-API-Key": os.environ["CARTESIA_API_KEY"],
        "Cartesia-Version": "2024-06-10",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the raw bytes to numpy array of float32
        audio_data = np.frombuffer(response.content, dtype=np.float32)

        # Normalize the float32 data to int16 range
        audio_data_int16 = (audio_data * 32767).astype(np.int16)

        # Open a new .wav file in write mode
        with wave.open("audio/response.wav", "wb") as wav_file:
            # Set the parameters for the .wav file
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 2 bytes per sample for 16-bit audio
            wav_file.setframerate(payload["output_format"]["sample_rate"])

            # Write the audio data
            wav_file.writeframes(audio_data_int16.tobytes())

        print("Audio saved as response.wav")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    return


def stream_audio(text):
    client = Cartesia(api_key=os.environ.get("CARTESIA_API_KEY"))
    # voice_name = "Barbershop Man"
    # voice_id = "a0e99841-438c-4a64-b679-ae501e7d6091"

    # Jarvis model id
    voice_id = "1d92e61c-e8a2-4544-9d17-b6dfb38e212a"
    voice = client.voices.get(id=voice_id)

    # transcript = "Hello! Welcome to Cartesia"

    # You can check out our models at https://docs.cartesia.ai/getting-started/available-models
    model_id = "sonic-english"

    # You can find the supported `output_format`s at https://docs.cartesia.ai/api-reference/endpoints/stream-speech-server-sent-events
    output_format = {
        "container": "raw",
        "encoding": "pcm_f32le",
        "sample_rate": 44100,
    }

    p = pyaudio.PyAudio()
    rate = 44100

    stream = None

    # Generate and stream audio
    for output in client.tts.sse(
        model_id=model_id,
        transcript=text,
        voice_embedding=voice["embedding"],
        stream=True,
        output_format=output_format,
    ):
        buffer = output["audio"]

        if not stream:
            stream = p.open(
                format=pyaudio.paFloat32, channels=1, rate=rate, output=True
            )

        # Write the audio data to the stream
        stream.write(buffer)

    stream.stop_stream()
    stream.close()
    p.terminate()


# test stream tts
# if __name__ == "__main__":
#     stream_audio("Hello, brandon.")


# test async tts
# get_audio_response("Hello, brandon.")
# if __name__ == "__main__":
#     while True:
#         mixer.init()
#         current_time = time()
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         print("Speaking...")
#         sound = mixer.Sound("audio/response.wav")
#         sound.play()
#         pygame.time.wait(int(sound.get_length() * 1000))
