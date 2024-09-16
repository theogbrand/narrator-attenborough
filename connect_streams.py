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


async def send_transcripts(ctx):
    # Check out voice IDs by calling `client.voices.list()` or on https://play.cartesia.ai/
    voice_id = "87748186-23bb-4158-a1eb-332911b0b708"

    # You can check out our models at https://docs.cartesia.ai/getting-started/available-models
    model_id = "sonic-english"

    # You can find the supported `output_format`s at https://docs.cartesia.ai/api-reference/endpoints/stream-speech-server-sent-events
    output_format = {
        "container": "raw",
        "encoding": "pcm_f32le",
        "sample_rate": 44100,
    }

    # transcripts = [
    #     "Sonic and Yoshi team up in a dimension-hopping adventure! ",
    #     "Racing through twisting zones, they dodge Eggman's badniks and solve ancient puzzles. ",
    #     "In the Echoing Caverns, they find the Harmonic Crystal, unlocking new powers. ",
    #     "Sonic's speed creates sound waves, while Yoshi's eggs become sonic bolts. ",
    #     "As they near Eggman's lair, our heroes charge their abilities for an epic boss battle. ",
    #     "Get ready to spin, jump, and sound-blast your way to victory in this high-octane crossover!"
    # ]

    response = completion(
        model="claude-3-5-sonnet-20240620",
        messages=[{"role": "user", "content": "tell me a joke"}],
        stream=True,
    )

    full_text = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            text_chunk = chunk.choices[0].delta.content
            if text_chunk.endswith(" "):
                full_text += text_chunk
            else:
                full_text += text_chunk + " "
            await ctx.send(
                model_id=model_id,
                transcript=text_chunk,
                voice_id=voice_id,
                continue_=True,
                output_format=output_format,
            )

    # for transcript in transcripts:
    #     # Send text inputs as they become available
    #     await ctx.send(
    #         model_id=model_id,
    #         transcript=transcript,
    #         voice_id=voice_id,
    #         continue_=True,
    #         output_format=output_format,
    #     )

    # Indicate that no more inputs will be sent. Otherwise, the context will close after 5 seconds of inactivity.
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


async def stream_and_listen():
    client = AsyncCartesia(api_key=os.environ.get("CARTESIA_API_KEY"))

    # Set up the websocket connection
    ws = await client.tts.websocket()

    # Create a context to send and receive audio
    ctx = ws.context()  # Generates a random context ID if not provided

    send_task = asyncio.create_task(send_transcripts(ctx))
    listen_task = asyncio.create_task(receive_and_play_audio(ctx))

    # Call the two coroutine tasks concurrently
    await asyncio.gather(send_task, listen_task)

    await ws.close()
    await client.close()


# asyncio.run(stream_and_listen())

# async def generate_and_speak(prompt):
#     response = completion(
#         model="claude-3-5-sonnet-20240620",
#         messages=[{"role": "user", "content": prompt}],
#         stream=True,
#     )

#     full_text = ""
#     for chunk in response:
#         if chunk.choices[0].delta.content:
#             text_chunk = chunk.choices[0].delta.content
#             if text_chunk.endswith(" "):
#                 full_text += text_chunk
#             else:
#                 full_text += text_chunk + " "
#             # Stream TTS for each chunk
#             # await stream_tts(text_chunk)

#     return full_text


# async def main():
#     while True:
#         user_input = input("\nEnter a message (or 'q' to exit): ")

#         if user_input.lower() == "q":
#             break

#         full_response = await generate_and_speak(user_input)
#         print("\nFull response:", full_response)


if __name__ == "__main__":
    asyncio.run(stream_and_listen())
