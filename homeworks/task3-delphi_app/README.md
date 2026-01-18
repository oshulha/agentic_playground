# Task 3 — Delphi-Based Multi-Expert Question Answering System

## Overview

This project implements a system that accepts a **complex question** and produces a **high-quality, well-structured, and comprehensive answer**.
The core logical foundation of the system is the **Delphi method**, adapted for use with Large Language Models.

The system automatically:

* Generates expert personas best suited to analyze the given question.
* Runs multiple Delphi rounds where experts independently reason, review each other’s perspectives, and refine their answers.
* Synthesizes the results into structured summaries.
* Estimates token usage and total API cost.

This implementation serves as a **baseline Delphi framework** and is intentionally extensible. The algorithmic behavior, expert dynamics, and aggregation logic can be further improved to achieve even higher-quality results.

---

## Key Concepts

* **Delphi Method** as the reasoning backbone
* **Self-generated expert personas**
* **Multi-round expert discussion**
* **Consensus-building via summaries**
* **Cost and token usage estimation**

---

## High-Level Delphi Flow

The Delphi process is implemented with **two rounds**:

1. **Round 1**

   * Experts independently answer the question.
2. **Round 2**

   * Experts receive a synthesized summary of Round 1.
   * Experts revise or expand their answers based on peer input.

Each round concludes with a structured summary.

---

## System Workflow

1. **User Input**

   * User submits a complex question via a web interface.

2. **Expert Generation**

   * The system dynamically generates `N` Delphi experts.
   * Each expert has:

     * A name
     * A profession
     * A thinking style
     * A short description of their value

3. **Expert Parsing**

   * Generated expert blocks (formatted as `№1. ...`) are parsed into an array for iteration.

4. **Round 1 — Independent Reasoning**

   * For each expert:

     * A role-specific system prompt is created.
     * The expert generates an independent response.
     * Responses are stored and appended to a conversation history.

5. **Round 1 Summary**

   * All expert responses are concatenated.
   * A summarization step extracts key ideas without revealing expert identities.

6. **Round 2 — Reflection & Revision**

   * Each expert:

     * Receives the Round 1 summary as user input.
     * Has their system prompt slightly modified (e.g., becoming more risk-seeking).
     * Produces a revised or expanded answer.
   * Responses are stored and appended to the conversation history.

7. **Round 2 Summary**

   * All second-round responses are concatenated.
   * A final summary is generated.

8. **Cost & Performance Estimation**

   * Token usage is calculated for:

     * Expert generation
     * Expert conversations
     * Summarization
   * Total execution time and estimated cost are reported.

---

## Project Structure

```
.
├── app.py
├── delphi.py
└── templates/
    └── index.html
```

---

## File Responsibilities

### `app.py`

* Flask-based web entry point.
* Handles:

  * User input submission
  * Triggering the Delphi process
  * Rendering the final result in the browser

---

### `delphi.py`

Core logic of the Delphi system, including:

* Expert persona generation
* Expert prompt construction
* Multi-round expert interaction
* Response aggregation and summarization
* Token counting and cost estimation
* Final result assembly

This file encapsulates the full Delphi reasoning pipeline.

---

### `templates/index.html`

* Minimal web interface
* Provides:

  * Text area for entering a complex question
  * Rendered HTML output of the Delphi results
* Optimized for readability of long, structured responses

---

## Delphi Logic Summary (Textual Diagram)

```
Start
  ↓
User inputs complex question
  ↓
Generate N experts
  ↓
Parse expert blocks into array
  ↓
For each expert:
  - Set system prompt
  - Call expert response (Round 1)
  - Save response
  ↓
Concatenate all responses
  ↓
Summarize Round 1
  ↓
Formulate follow-up user input
  ↓
For each expert:
  - Modify system prompt (e.g., risk-seeking)
  - Add summary as user message
  - Call expert response (Round 2)
  - Save response
  ↓
Concatenate all responses
  ↓
Summarize Round 2
  ↓
Estimate token usage and cost
  ↓
Final output
```

> A visual draft of this flow can be found in `task3_delphi.drawio`.
> The diagram was created quickly and is not fully polished, but it mirrors the textual explanation above.

---

## Design Notes

* Expert identities are **not revealed** during summarization.
* Conversations are isolated per expert to preserve independent reasoning.
* The system is intentionally modular to allow:

  * More rounds
  * Different expert interaction strategies
  * Alternative aggregation methods

---

## Intended Use Cases

* Complex analytical questions
* Multi-disciplinary reasoning
* Decision support systems
* Research assistance
* Strategy synthesis

---

## Extensibility

Possible future improvements include:

* Dynamic round count
* Expert weighting
* Contrarian or adversarial experts
* Automatic stopping based on convergence
* Improved consensus detection

---

## Requirements

* Python 3.x
* Flask
* OpenAI API key
* Internet connection

---

## Disclaimer

This project is a **research and experimentation framework** demonstrating how the Delphi method can be adapted for LLM-based systems. It is not intended as a final or optimal implementation.

---

## Usage

To run the system, simply execute python app.py. The web interface will start, and you can access it in your browser at http://127.0.0.1:5000.