import os
from litellm import completion
import base64
import time
import simpleaudio as sa
import errno
from elevenlabs import generate, play, set_api_key, voices
import argparse
import dotenv
import tts
import pygame
from time import time
import asyncio
from pygame import mixer


dotenv.load_dotenv()
from dotenv import load_dotenv

# Attempt to load environment variables from .env file
if not load_dotenv():
    print("Warning: .env file not found or empty. Using default environment variables.")

# Remove the OpenAI client initialization
# client = OpenAI()

# set_api_key(os.environ.get("ELEVENLABS_API_KEY"))


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


# def play_audio(text):
#     audio = generate(text, voice=os.environ.get("ELEVENLABS_VOICE_ID"))

#     unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
#     dir_path = os.path.join("narration", unique_id)
#     os.makedirs(dir_path, exist_ok=True)
#     file_path = os.path.join(dir_path, "audio.wav")

#     with open(file_path, "wb") as f:
#         f.write(audio)

#     play(audio)


# def analyze_image(base64_image, message_history, model):
#     system_content = """
#     You are an expert data analyst. You are given a screenshot of diagrams from a research paper and a series of questions.
#     """

#     messages = [
#         {
#             "role": "system",
#             "content": system_content,
#         },
#     ] + message_history + [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "Describe this image"},
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{base64_image}"
#                     },
#                 },
#             ],
#         },
#     ]

#     response = completion(
#         model=model,
#         messages=messages,
#         max_tokens=500,
#     )
#     response_text = response.choices[0].message.content
#     return response_text
1

import json
from prompts import (
    super_flattened_o1_content_dict,
    o1_summary,
)

from litellm import completion
import os
import dotenv

dotenv.load_dotenv()


def get_relevant_sections(question):
    prompt = f"""Given the following question:

    <question>
    {question}
    </question>

    Please analyze the content in the super_flattened_o1_content_dict and return the most relevant sections that would be helpful in answering this question. Before answering, explain your reasoning step-by-step in the chain_of_thought key. Respond ONLY in a JSON object with the following structure:

    {{
        "relevant_sections": [
            {{
                "chain_of_thought": "A brief explanation of why this section_key is relevant to answering the question provided above",
                "section_key": "Key of the relevant section or subsection which corresponds to a value containing text in super_flattened_o1_content_dict."
            }},
            ...
        ],
    }}

    Here is the super_flattened_o1_content_dict:

    <super_flattened_o1_content_dict>
    {json.dumps(super_flattened_o1_content_dict, indent=2)}
    </super_flattened_o1_content_dict>
    """
    claude_response = generate_llm_response(prompt)

    return claude_response


def generate_llm_response(prompt):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_relevant_sections",
                "description": "Get relevant sections from a document based on a given query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relevant_sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "chain_of_thought": {
                                        "type": "string",
                                        "description": "Explanation of why this section is relevant to the query",
                                    },
                                    "section_key": {
                                        "type": "string",
                                        "description": "The key or identifier of the relevant section",
                                    },
                                },
                                "required": ["chain_of_thought", "section_key"],
                            },
                        }
                    },
                    "required": ["relevant_sections"],
                },
            },
        }
    ]

    try:
        response = completion(
            model="claude-3-5-sonnet-20240620",
            messages=[
                {"role": "user", "content": prompt},
            ],
            tool_choice={
                "type": "function",
                "function": {"name": "get_relevant_sections"},
            },
            temperature=0.0,
            tools=tools,
        )

        claude_response = response.choices[0].message.tool_calls[0].function.arguments
        return claude_response
    except Exception as e:
        print(f"An error occurred producing JSON response: {str(e)}")
        return None


def get_relevant_section_content(retrieved):
    # insert function to flatten the section_key values into a single array containing section_keys
    retrieved_json = json.loads(retrieved)
    flattened_section_keys = []
    for section in retrieved_json["relevant_sections"]:
        flattened_section_keys.append(section["section_key"])

    # get the content of the section_keys
    relevant_content = []
    for section_key in flattened_section_keys:
        relevant_content.append(
            {section_key: super_flattened_o1_content_dict[section_key]}
        )

    return relevant_content


def synthesize_response(user_input, flattened_section_content, base64_image):
    flattened_section_content_str = json.dumps(flattened_section_content)
    prompt = f"""
    Given the following question:

    <question>
    {user_input}
    </question>

    And the following relevant sections:

    <relevant_sections>
    {flattened_section_content_str}
    </relevant_sections>

    Please synthesize a response to the question using the relevant sections and the image.
    """
    # print("final prompt: ", prompt)

    #  {
    #             "role": "user",
    #             "content": [
    #                 {"type": "text", "text": "Describe this image"},
    #                 {
    #                     "type": "image_url",
    #                     "image_url": {
    #                         "url": f"data:image/jpeg;base64,{base64_image}"
    #                     },
    #                 },
    #             ],
    #         },
    response = completion(
        model="claude-3-5-sonnet-20240620",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        max_tokens=1000,
        temperature=0.0,
    )
    return response.choices[0].message.content


def simplify_response(llm_output):
    prompt = f"""
    Given the following response:

    <response>
    {llm_output}
    </response>

    Please simplify the response to a more concise and clear format.
    """
    response = completion(
        model="claude-3-5-sonnet-20240620",
        system="You are an expert teacher of explaining complex AI concepts in simple terms. You are given a response from a large language model and you must simplify it to a conversational answer, like how a great teacher like Richard Feynman would explain a complex physics concept to his students. Only respond with the simplified response. REMEMBER, be conversational and engaging, but do not lose the critical scientific details. Explain using the Pyramid Principle when appropriate. Do not use analogies too much. Do not answer in a list format.",
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.0,
    )
    return response.choices[0].message.content


def synthesize_response_with_summary_and_prompt_question_to_user(
    user_input, explanation, summary, message_history
):
    prompt = f"""
    Given the following question:

    <question>
    {user_input}
    </question>
    
    And the following explanation:

    <explanation>
    {explanation}
    </explanation>

    And the following summary:

    <summary>
    {summary}
    </summary>

     First, prompt the user to clarify if their question was answered by the explanation. Then, please synthesize all of the above into a single follow up question that will continue the train of thought the user was on to understand the big picture and core takeaways of the summary. Do not mention being provided the summary, explanation, or question. Just respond with the follow up question ONLY.
    """

    response = completion(
        model="claude-3-5-sonnet-20240620",
        system="You are an expert teacher who is great at engaging students and prompting them to think more deeply about a concept.",
        messages=message_history
        + [
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.0,
    )
    return response.choices[0].message.content


def main():
    """
    Main function to run the conversational loop.
    """
    print(
        "Welcome! Ask me anything about the Persona-Driven Data Synthesis Methodology."
    )

    message_history = []
    while True:
        mixer.init()
        current_time = time()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        user_input = input("\nEnter a message (or 'q' to exit): ")

        if user_input.lower() == "q":
            print("Thank you for using the system. Goodbye!")
            break

        print("JARVIS is working...")

        fetched_relevant_sections_array = get_relevant_sections(user_input)
        flattened_section_content = get_relevant_section_content(
            fetched_relevant_sections_array
        )

        print("JARVIS is synthesizing with visual input...")
        image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

        # getting the base64 encoding
        base64_image = encode_image(image_path)
        response = synthesize_response(
            user_input, flattened_section_content, base64_image
        )
        final_explanation = simplify_response(response)

        follow_up_question = (
            synthesize_response_with_summary_and_prompt_question_to_user(
                user_input, final_explanation, o1_summary, message_history
            )
        )

        # Concatenate the final explanation and follow-up question
        output = f"{final_explanation}\n\n{follow_up_question}"
        print("\nResponse:", output)

        current_time = time()
        tts.get_audio_response(output)
        audio_time = time() - current_time
        print(f"Finished generating audio in {audio_time:.2f} seconds.")

        print("Speaking...")
        sound = mixer.Sound("audio/response.wav")
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))

        message_history.append({"role": "user", "content": user_input})
        message_history.append({"role": "assistant", "content": output})

        print("\nMessage History:", message_history)


if __name__ == "__main__":
    main()

# def main():
#     message_history = []

#     # Parse command-line arguments
#     parser = argparse.ArgumentParser(description="Vrag")
#     parser.add_argument("--model", default="gpt-4-vision-preview", help="Vision model to use (default: gpt-4-vision-preview)") # gpt-4o, claude-3.5-sonnet, gemini-1.5-pro-latest
#     args = parser.parse_args()

#     while True:
#         # path to your image
#         image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

#         # getting the base64 encoding
#         base64_image = encode_image(image_path)

#         # analyze image
#         print(f"👀 JARVIS is watching using {args.model}...")
#         analysis = analyze_image(base64_image, message_history=message_history, model=args.model)

#         print("🎙️ JARVIS says:")
#         print(analysis)

#         # play_audio(analysis)

#         message_history = message_history + [{"role": "assistant", "content": analysis}]

#         # wait for 5 seconds
#         time.sleep(5)


# if __name__ == "__main__":
#     main()
