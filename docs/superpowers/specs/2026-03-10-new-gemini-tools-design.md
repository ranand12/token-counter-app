# New Gemini API Tools — Design Spec

## Overview
Add 7 new standalone HTML tool pages to the Gemini Tools app, each showcasing a distinct Gemini API capability. All pages follow the existing pattern: self-contained HTML + inline CSS/JS, shared nav, pre-populated inputs, zero-friction UX.

## Design Principles
- Pre-populate everything: model, prompts, options
- Preset buttons for common use cases
- Toggles and sliders instead of manual config
- Users see the capability without having to think or configure

## New Tools

### 1. `tts.html` — Text-to-Speech
- **Model:** `gemini-2.5-flash-preview-tts`
- **API:** `POST v1beta/models/gemini-2.5-flash-preview-tts:generateContent`
- **Request body:** `responseModalities: ["AUDIO"]`, `speechConfig` with `prebuiltVoiceConfig`
- **UI:** Voice picker dropdown (Kore, Charon, Fenrir, Aoede, Puck, etc.), pre-filled text, preset buttons (Storytelling, News Anchor, Cheerful Greeting, Dramatic Reading), `<audio>` player + download button
- **Response:** Base64 audio in `inlineData`, decoded to audio blob

### 2. `think.html` — Thinking Mode
- **Model:** `gemini-2.5-flash`
- **API:** `POST v1beta/models/{model}:generateContent`
- **Request body:** `generationConfig.thinkingConfig: { includeThoughts: true, thinkingBudget: N }`
- **UI:** Budget slider (0–24576), preset prompts (Math Puzzle, Logic Riddle, Code Debug, Science), two-panel result (collapsible thought process + final answer), token counts
- **Response:** Parts array with `thought: true` parts and regular parts

### 3. `code.html` — Code Execution
- **Model:** `gemini-2.5-flash`
- **API:** `POST v1beta/models/{model}:generateContent`
- **Request body:** `tools: [{ code_execution: {} }]`
- **UI:** Pre-filled prompt, presets (Fibonacci, Prime Sieve, Data Analysis, Math Proof, String Manipulation), three-section result (explanation, generated code, execution output)
- **Response:** Parts with `executableCode` and `codeExecutionResult`

### 4. `url.html` — URL Context
- **Model:** `gemini-2.5-flash`
- **API:** `POST v1beta/models/{model}:generateContent`
- **Request body:** `tools: [{ url_context: {} }]`
- **UI:** URL input pre-filled with sample, question textarea, presets (Summarize, Extract Facts, Find Dates, Compare)
- **Response:** Standard text response with grounding from URL content

### 5. `maps.html` — Google Maps
- **Model:** `gemini-2.5-flash`
- **API:** `POST v1beta/models/{model}:generateContent`
- **Request body:** `tools: [{ googleMaps: {} }]`, `toolConfig.retrievalConfig.latLng`
- **UI:** "Use My Location" button + city picker dropdown, question textarea, presets (Coffee Shops, Restaurants, Parks, Museums, Hotels)
- **Response:** Text with place details from Maps grounding

### 6. `research.html` — Deep Research
- **Model/Agent:** `deep-research-pro-preview-12-2025`
- **API:** `POST v1beta/interactions` (create), `GET v1beta/interactions/{id}` (poll)
- **Request body:** `{ input: "...", agent: "deep-research-pro-preview-12-2025", background: true }`
- **UI:** Pre-filled topic, presets (Quantum Computing, AI Safety, Climate Tech, Space Exploration), polling progress indicator, full research report with citations, warning about 1-5 min wait
- **Response:** Poll until `state: "COMPLETED"`, then display `output`

### 7. `files.html` — File Search
- **Model:** `gemini-2.5-flash`
- **API:** `POST v1beta/files` (upload), then `POST v1beta/models/{model}:generateContent` with file URI
- **UI:** Drop zone for documents (PDF, TXT, CSV), pre-filled question, presets (Summarize, Extract Data, Find Dates, Q&A)
- **Response:** Standard text response grounded in uploaded file

## Shared Changes
- Update nav links in ALL existing HTML pages to include 7 new tools
- New nav entries: TTS, Think, Code, URL, Maps, Research, Files

## CSP Updates
Each new page needs appropriate CSP meta tag. All pages need `connect-src https://generativelanguage.googleapis.com`. TTS page also needs `media-src blob: data:` for audio playback.
