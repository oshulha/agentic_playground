#версія з локальним збереженням
import sounddevice as sd
from scipy.io.wavfile import write
import keyboard
import numpy as np
import time
import os
from openai import OpenAI

# Параметри запису
SAMPLE_RATE = 44100  # Гц

is_recording = False
recorded_data = []

def start_or_stop_recording():
    global is_recording, recorded_data
    if not is_recording:
        print("🎙️ Початок запису... Натисни Ctrl+Shift+R ще раз для зупинки.")
        recorded_data = []
        is_recording = True
        global aud_stream
        aud_stream = sd.InputStream(callback=audio_callback, samplerate=SAMPLE_RATE, channels=2)
        aud_stream.start()
    else:
        print("⏹️ Зупинка запису...")
        is_recording = False
        aud_stream.stop()
        save_recording()

def audio_callback(indata, frames, time_info, status):
    if is_recording:
        recorded_data.append(indata.copy())

def save_recording():
    global recorded_data, filename
    if recorded_data:
        audio = np.concatenate(recorded_data, axis=0)
        filename = f"voice_{int(time.time())}.wav"
        write(filename, SAMPLE_RATE, audio)
        print(f"✅ Файл збережено: {os.path.abspath(filename)}")
    else:
        print("⚠️ Немає даних для збереження.")

def listen_keys():
    keyboard.add_hotkey('ctrl+shift+r', start_or_stop_recording)
    print("🟢 Натисни Ctrl + Shift + R для початку/зупинки запису.")
     # Очікуємо, поки запис не завершиться
    while is_recording or not recorded_data:
        time.sleep(0.1)  # Чекаємо, поки запис завершиться

# if __name__ == "__main__":
listen_keys()

# client = OpenAI(
#    api_key="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"
# )

# audio_file= open(filename, "rb")

# transcription = client.audio.transcriptions.create(
#     model="whisper-1", 
#     file=audio_file
# )

# #also can try smth like gpt-4o-transcribe or gpt-4o-mini-transcribe to see if can recognize voice better than whisper-1

# print("Transcription" + transcription.text)

# translation = client.audio.translations.create(
#     model="whisper-1", 
#     file=audio_file
# )

# print("Translation" + translation.text)

client = OpenAI(api_key="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")
audio_file = open(filename, "rb")

translation = client.audio.translations.create(
    model="whisper-1", 
    file=audio_file
)

raw_translation = translation.text

print("Translation " + translation.text)

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
            {"role": "user", "content": translation_text}
        ]
    )
    return response.choices[0].message.content

corrected_text = generate_corrected_translation(
    0, system_prompt, raw_translation
)

print(corrected_text)
