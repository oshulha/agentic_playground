# Task 2 — Voice Recording, Transcription, Cleaning, and Translation Utility

## Overview

This project implements a utility that is activated via a global hotkey and starts recording your voice (in any language convenient for you) until you manually stop it. After stopping the recording, the program:

1. Transcribes the audio using OpenAI Whisper.
2. Cleans the transcription from filler sounds, stuttering, and transcription artifacts.
3. Translates the final text into high-quality English.

The project is designed as a **single-file utility** with two interchangeable implementations.

---

## Project Structure

This is a **single-file project** with two versions:

* **`task2_main_microphone.py`** (main version)

  * Saves the final processed text directly to the **system clipboard**.

* **`task2_saves_locally.py`**

  * Saves the recorded audio **locally** as a `.wav` file in a directory.

Aside from the output destination (clipboard vs local file), both implementations are **functionally identical**.

---

## Usage

1. Run one of the Python files:

   ```bash
   python task2_main_microphone.py
   ```

   or

   ```bash
   python task2_saves_locally.py
   ```

2. After launch, the program prints instructions in the terminal.

3. Use the global hotkey to control recording:

   * **Start / Stop recording:** `Ctrl + Shift + R`

4. The audio is processed automatically after recording stops.

---

## Processing Pipeline
**Also, you can found structure in task2_microphone.drawio but it's done fast and not good enough. However, explains like a text below**
1. **Audio Capture**

   * Voice is recorded from the microphone until manually stopped.

2. **Speech-to-Text & Translation**

   * Audio files are sent to **OpenAI Whisper API**.
   * Whisper performs transcription and **immediate translation to English**.

3. **Text Cleaning**

   * The translated English text is passed to **`gpt-4.1-nano`**, which:

     * Removes filler words (e.g., “uh”, “um”).
     * Fixes stuttering and repetition.
     * Cleans up transcription artifacts.

---

## Alternative (More Direct) Approach

A potentially more effective approach is also considered:

* Whisper **does not translate**, but only returns the **original-language transcription**.
* `gpt-4.1-nano` then:

  * Cleans the text.
  * Translates it into English in a single step.

This approach may yield higher-quality results, depending on the input language and speech patterns.

---

## Cost Tracking

The utility tracks and reports:

* **Recording duration**
* **Whisper costs**
* **`gpt-4.1-nano` input token costs**
* **`gpt-4.1-nano` output token costs**
* **Total cost per recording**

This makes it easy to evaluate and optimize usage.

---

## Requirements

* Python 3.x
* Microphone access
* OpenAI API key configured in the environment
* Required Python dependencies (as specified in the script)

---

## Notes

* No additional configuration is required beyond running the Python file.
* The project is designed for simplicity and fast iteration.
* Suitable for quick voice-to-English workflows, note-taking, and command-style dictation.

---
