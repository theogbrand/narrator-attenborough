import os
from litellm import completion
from cartesia import Cartesia
import asyncio
import pyaudio

# Initialize Cartesia client
cartesia_client = Cartesia(api_key=os.environ.get("CARTESIA_API_KEY"))


# async def stream_tts(text):
#     voice_id = (
#         "1d92e61c-e8a2-4544-9d17-b6dfb38e212a"  # Replace with your desired voice ID
#     )
#     model_id = "sonic-english"  # Or your preferred model

#     client = Cartesia(api_key=os.environ.get("CARTESIA_API_KEY"))
#     voice = client.voices.get(id=voice_id)

#     # You can check out our models at https://docs.cartesia.ai/getting-started/available-models
#     model_id = "sonic-english"

#     output_format = {
#         "container": "raw",
#         "encoding": "pcm_f32le",
#         "sample_rate": 44100,
#     }

#     p = pyaudio.PyAudio()
#     rate = 44100

#     stream = None

#     # Set up the websocket connection
#     ws = client.tts.websocket()

#     # Generate and stream audio using the websocket
#     for output in ws.send(
#         model_id=model_id,
#         transcript=chunk_generator(text),
#         voice_embedding=voice["embedding"],
#         stream=True,
#         output_format=output_format,
#     ):
#         buffer = output["audio"]

#         if not stream:
#             stream = p.open(
#                 format=pyaudio.paFloat32, channels=1, rate=rate, output=True
#             )

#         # Write the audio data to the stream
#         stream.write(buffer)

#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     ws.close()  # Close the websocket connection
#     return


import asyncio
import os
import pyaudio
from cartesia import AsyncCartesia


async def send_transcripts(ctx, prompt, system_prompt, message_history: list = []):
    voice_id = "87748186-23bb-4158-a1eb-332911b0b708"
    model_id = "sonic-english"
    output_format = {
        "container": "raw",
        "encoding": "pcm_f32le",
        "sample_rate": 44100,
    }

    response = completion(
        model="claude-3-5-sonnet-20240620",
        system=system_prompt,
        messages=message_history + [{"role": "user", "content": prompt}],
        stream=True,
        temperature=0.0,
        max_tokens=1000,
    )

    full_text = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            text_chunk = chunk.choices[0].delta.content
            if text_chunk.endswith(" "):
                full_text += text_chunk
            else:
                full_text += text_chunk + " "
            print(text_chunk)
            await ctx.send(
                model_id=model_id,
                transcript=text_chunk,
                voice_id=voice_id,
                continue_=True,
                output_format=output_format,
                _experimental_voice_controls={
                    "speed": "fastest",
                },
            )

    await ctx.no_more_inputs()


async def receive_and_play_audio(ctx):
    p = pyaudio.PyAudio()
    stream = None
    rate = 44100

    async for output in ctx.receive():
        buffer = output["audio"]

        if not stream:
            stream = p.open(
                format=pyaudio.paFloat32, channels=1, rate=rate, output=True
            )

        stream.write(buffer)

    stream.stop_stream()
    stream.close()
    p.terminate()


async def stream_and_listen(
    prompt: str, system_prompt: str = "", message_history: list = []
):
    client = AsyncCartesia(api_key=os.environ.get("CARTESIA_API_KEY"))

    ws = await client.tts.websocket()
    ctx = ws.context()

    send_task = asyncio.create_task(
        send_transcripts(ctx, prompt, system_prompt, message_history)
    )
    listen_task = asyncio.create_task(receive_and_play_audio(ctx))

    await asyncio.gather(send_task, listen_task)

    await ws.close()
    await client.close()

    return


# if __name__ == "__main__":
#     user_prompt = input("Enter your prompt: ")
#     asyncio.run(stream_and_listen(user_prompt))
