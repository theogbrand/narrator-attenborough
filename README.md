# David Attenborough narrates your life. 

https://twitter.com/charliebholtz/status/1724815159590293764

## Want to make your own AI app?
Check out [Replicate](https://replicate.com). We make it easy to run machine learning models with an API.

## Setup

Clone this repo, and setup and activate a virtualenv:

```bash
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
```

Then, install the dependencies:
`pip install -r requirements.txt`

```
export OPENAI_API_KEY=<token>
export ELEVENLABS_API_KEY=<eleven-token>
```

Make a new voice in Eleven and get the voice id of that voice using their [get voices](https://elevenlabs.io/docs/api-reference/voices) API, or by clicking the flask icon next to the voice in the VoiceLab tab.

```
export ELEVENLABS_VOICE_ID=jB2lPb5DhAX6l1TLkKXy
```

## Run it!

In on terminal, run the webcam capture:
```bash
python capture.py --mode screenshot
```
In another terminal, run the narrator:

```bash
python narrator.py --mode screenshot --model claude-3-5-sonnet-20240620, gpt-4o, gemini/gemini-1.5-pro
```

run without flag for webcam mode


Notes:
* Feeling when don't quite get it when re-read papers, but when the OP distills a complex paper into super crisp and clear explanations
    * even better, having a conversation with OP internalises knowledge even better (Active Learning)
    * scale this experience, reduce time to most important insight
    * address innate desire to acquire insights
* shortest path to second order insights