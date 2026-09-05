# Prototype Limitations & Engineering Disclosures

**Project:** AI Teacher: Build a Human-Like AI Educator That Teaches Through Video  
**Role:** AGENT 10 — Integration, Demo Orchestration & Documentation

---

## 1. Overview

In accordance with rigorous hackathon and engineering evaluation standards, this document outlines the current technical boundaries, architectural constraints, and realistic trade-offs of the AI Teacher prototype. These constraints represent standard boundaries of a high-speed, local-first hackathon prototype rather than system failures.

---

## 2. Technical Limitation Categories

### 2.1 Multi-Modal Video & Avatar Rendering
- **Vector-Based SVG Canvas vs Photorealistic Video Generation:**
  - *Current Prototype:* The live frontend utilizes a custom SVG vector animation engine featuring dynamic breathing, randomized blinking, phoneme-driven mouth movement, and coordinate-directed laser pointing.
  - *Trade-off:* While this provides instantaneous rendering, 60fps interaction, zero video buffer latency, and zero cloud GPU costs, it does not produce photorealistic human skin textures like commercial video APIs (e.g. HeyGen or D-ID).
  - *Backend Integration:* The backend exposes `POST /api/video/generate` and `POST /api/avatar/generate` ready to integrate external cloud diffusion video pipelines for asynchronous offline video rendering.

### 2.2 Voice & Audio Synthesis
- **Client-Side Web Speech API vs Custom Neural Cloning:**
  - *Current Prototype:* Speech is driven by the host browser's native W3C Web Speech API.
  - *Trade-off:* Voice quality and Hindi/Hinglish phonetic realism depend on the host operating system's installed speech voices (e.g., Microsoft Natural voices on Windows 11 produce high fidelity, whereas minimal Linux containers may fall back to robotic espeak).
  - *Mitigation:* The system includes dialogue transcripts and whiteboard subtitles to guarantee complete pedagogical accessibility regardless of audio hardware.

### 2.3 Document Intelligence & OCR
- **Text-Based PDF Extraction vs Scanned Handwritten Document OCR:**
  - *Current Prototype:* The RAG subsystem utilizes `pypdf` for digital PDF, DOCX, and TXT documents.
  - *Trade-off:* Scanned PDF documents consisting purely of raster images without embedded OCR text layers will yield empty text extractions unless pre-processed with an external OCR engine (like Tesseract).

### 2.4 Knowledge Scope (Topic-Only Mode)
- **STEM & Algorithmic Curricula Focus:**
  - *Current Prototype:* Curated high-fidelity pedagogical graphs, interactive simulations, and misconception diagnostic matrices are implemented for core physics (*Ohm's Law, DC Circuits*) and computer science (*Binary Search, Algorithmic Analysis*).
  - *Trade-off:* When an arbitrary non-canonical topic is requested without uploaded materials (e.g. *Ancient Roman History*), the system relies on LLM prompt synthesis (`gemini-3.7-flash` / `gemini-3.6-flash`), which falls back to generalized concept maps rather than domain-specific animated physics simulations.

### 2.5 Open-Ended Evaluation Nuance
- **Semantic Diagnosis vs Ambiguous Student Input:**
  - *Current Prototype:* Agent 6 evaluates student reasoning using a combination of keyword/pattern detection (for canonical misconceptions) and LLM classification.
  - *Trade-off:* Extremely brief or ambiguous answers (e.g. a single punctuation mark or random keystroke) are classified as incomplete responses and prompt a clarifying follow-up rather than a specific misconception diagnosis.

### 2.6 Language Coverage
- **English, Hindi, and Hinglish:**
  - *Current Prototype:* The multilingual engine (Agent 8) focuses on English, standard Hindi, and colloquial Hinglish (the predominant mode of instruction in South Asian technical education).
  - *Trade-off:* Regional Indic languages (Tamil, Telugu, Bengali) and non-Indic languages (Spanish, Mandarin) are not yet integrated into the diagnostic rules.

---

## 3. Scalability & Production Roadmap

| Current Prototype State | Target Production Evolution |
|---|---|
| In-memory keyword & TF/IDF chunk retrieval | Persistent Qdrant or Milvus vector cluster with hybrid dense-sparse reranking |
| Browser-native Web Speech API | Fine-tuned multi-dialect Edge-TTS or ElevenLabs multilingual voice model |
| Animated SVG avatar on HTML5 Canvas | Hybrid SVG real-time interaction + Pre-rendered 4K Sora/Runway video scenes |
| Local SQLite learner profile storage | Distributed PostgreSQL with Redis caching for multi-tenant classroom deployments |
