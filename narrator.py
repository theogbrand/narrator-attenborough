import os
from litellm import completion
import base64
import time
import simpleaudio as sa
import errno
from elevenlabs import generate, play, set_api_key, voices
import argparse
import dotenv

dotenv.load_dotenv()
from dotenv import load_dotenv

# Attempt to load environment variables from .env file
if not load_dotenv():
    print("Warning: .env file not found or empty. Using default environment variables.")

# Remove the OpenAI client initialization
# client = OpenAI()

set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)


def play_audio(text):
    audio = generate(text, voice=os.environ.get("ELEVENLABS_VOICE_ID"))

    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    play(audio)


def analyze_image(base64_image, script, mode, model):
    system_content = """
    You are Sir David Attenborough. Narrate the {mode} as if it is a nature documentary.
    Make it snarky and funny. Don't repeat yourself. Make it short. If you see anything remotely interesting, make a big deal about it!
    {focus}
    """.format(
        mode="webcam footage of the human" if mode == "webcam" else "screenshot of the human's computer",
        focus="Focus on the person's appearance, posture, and surroundings." if mode == "webcam" else "Focus on the activities, applications, and content visible on the screen."
    )

    messages = [
        {
            "role": "system",
            "content": system_content,
        },
    ] + script + [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ],
        },
    ]

    response = completion(
        model=model,
        messages=messages,
        max_tokens=500,
    )
    response_text = response.choices[0].message.content
    return response_text


def main():
    script = []
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Narrate webcam or screenshot")
    parser.add_argument("--mode", choices=["webcam", "screenshot"], default="webcam", help="Capture mode (default: webcam)")
    parser.add_argument("--model", default="gpt-4-vision-preview", help="Vision model to use (default: gpt-4-vision-preview)") # gpt-4o, claude-3.5-sonnet, gemini-1.5-pro-latest
    args = parser.parse_args()

    while True:
        # path to your image
        image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

        # getting the base64 encoding
        base64_image = encode_image(image_path)

        # analyze image
        print(f"👀 Aya is watching using {args.model}...")
        analysis = analyze_image(base64_image, script=script, mode=args.mode, model=args.model)

        print("🎙️ Aya says:")
        print(analysis)

        play_audio(analysis)

        script = script + [{"role": "assistant", "content": analysis}]

        # wait for 5 seconds
        time.sleep(5)


if __name__ == "__main__":
    main()
