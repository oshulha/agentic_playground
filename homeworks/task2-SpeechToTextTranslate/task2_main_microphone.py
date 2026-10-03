import sounddevice as sd
import numpy as np
import time
import io
import base64
import keyboard
import pyperclip
import os
from openai import OpenAI
import scipy.io.wavfile as wavfile
import tiktoken  # For token estimation

SAMPLE_RATE = 44100
is_recording = False
recorded_data = []


def start_or_stop_recording():
    global is_recording, recorded_data, audio_duration
    if not is_recording:
        print("🎙️ Start recording... Press Ctrl+Shift+R again to stop.")
        recorded_data = []
        is_recording = True
        global aud_stream
        aud_stream = sd.InputStream(
            callback=audio_callback, samplerate=SAMPLE_RATE, channels=2
        )
        aud_stream.start()
    else:
        print("⏹️ Stop recording...")
        is_recording = False
        aud_stream.stop()
        audio_duration = save_recording_to_clipboard()


def audio_callback(indata, frames, time_info, status):
    if is_recording:
        recorded_data.append(indata.copy())


def save_recording_to_clipboard():
    if recorded_data:
        audio = np.concatenate(recorded_data, axis=0)
        duration_sec = len(audio) / SAMPLE_RATE

        memfile = io.BytesIO()
        wavfile.write(memfile, SAMPLE_RATE, audio)
        memfile.seek(0)

        b64_audio = base64.b64encode(memfile.read()).decode("utf-8")
        pyperclip.copy(b64_audio)

        print(
            f"✅ Audio ({duration_sec:.2f} sec) is saved to the clipboard in Base64 format."
        )
        return duration_sec
    else:
        print("⚠️ No data to save.")
        return 0


def listen_keys():
    keyboard.add_hotkey("ctrl+shift+r", start_or_stop_recording)
    print("🟢 Press Ctrl + Shift + R for start/stop recording.")
    # Wait until recording starts
    while not is_recording and not recorded_data:
        time.sleep(0.1)
    # Wait until recording stops
    while is_recording:
        time.sleep(0.1)


listen_keys()

# Add a small delay to ensure clipboard is updated
time.sleep(0.2)
b64_audio = pyperclip.paste()
audio_bytes = base64.b64decode(b64_audio)

audio_file = io.BytesIO(audio_bytes)
audio_file.name = "audio.wav"  # The Whisper API requires a .name


start = time.perf_counter()
client = OpenAI(
    api_key="OPENAI_API_KEY"
)

translation = client.audio.translations.create(model="whisper-1", file=audio_file)

raw_translation = translation.text

# print("Translation " + translation.text)

# 2. GPT-4.1 nano post-processing

system_prompt = """
Your task is to clean up a transcribed English text. Improve clarity and correctness by performing the following actions:

1. Remove filler words and hesitation sounds such as "um", "uh", "like", "you know", "I mean", "sort of", "kind of", "basically", "actually", "literally", "so", "well", "okay", "right", "yeah", "hmm", and similar.
2. Correct any grammar, spelling, or punctuation mistakes.
3. Remove redundant words or repeated phrases that do not add meaning.
4. Standardize terminology to align with contemporary usage. For example, use "cybersecurity" (one word) instead of "cyber security" (two words).
5. Preserve the original length, structure, and phrasing of the text as much as possible.
6. Maintain the speaker's original intent, tone, and voice.
7. Only use the context provided; do not infer or add information not present in the original text.

Output the cleaned-up version of the text in plain, fluent English.
"""


def generate_corrected_translation(temperature, system_prompt, translation_text):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": translation_text},
        ],
    )
    return response.choices[0].message.content


corrected_text = generate_corrected_translation(0, system_prompt, raw_translation)

print("\nTranslation: " + corrected_text)

end = time.perf_counter()  # can be inserted before print and display less time

elapsed = end - start

print(f"\nExecution time: {elapsed:.4f} seconds")

whisper_cost = (audio_duration / 60) * 0.006

# GPT token counting
enc = tiktoken.encoding_for_model("gpt-4")  # approximate GPT-4.1 Nano

input_tokens = len(enc.encode(system_prompt)) + len(enc.encode(raw_translation))
output_tokens = len(enc.encode(corrected_text))

gpt_input_cost = (input_tokens / 1_000_000) * 0.10
gpt_output_cost = (output_tokens / 1_000_000) * 0.40
gpt_total_cost = gpt_input_cost + gpt_output_cost

total_cost = whisper_cost + gpt_total_cost

print("\n COST ESTIMATE:")
print(f" - Whisper API:        ${whisper_cost:.6f}")
print(f" - GPT Input Tokens:   {input_tokens} → ${gpt_input_cost:.6f}")
print(f" - GPT Output Tokens:  {output_tokens} → ${gpt_output_cost:.6f}")
print(f" = Total Estimated:    ${total_cost:.6f}")
