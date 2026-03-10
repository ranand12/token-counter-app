# New Gemini API Tools Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 7 new standalone HTML tool pages (TTS, Thinking, Code Execution, URL Context, Google Maps, Deep Research, File Search) to the Gemini Tools app.

**Architecture:** Each tool is a self-contained HTML file following the existing pattern (inline CSS + JS, shared nav via nav.css/nav.js). All pages pre-populate inputs, use preset buttons, and minimize user effort. Nav sidebar updated centrally in nav.js.

**Tech Stack:** Vanilla HTML/CSS/JS, Gemini REST API (v1beta), no build tools.

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `nav.js` | Modify (lines 7-28) | Add 7 new tools to sidebar sections array |
| `tts.html` | Create | Text-to-speech with voice picker and audio playback |
| `think.html` | Create | Thinking mode with budget slider and thought display |
| `code.html` | Create | Code execution with syntax display |
| `url.html` | Create | URL context summarization |
| `maps.html` | Create | Google Maps grounding with geolocation |
| `research.html` | Create | Deep Research with polling |
| `files.html` | Create | File upload and Q&A |

## Template Pattern (all pages follow this)

Every page uses this exact structure from existing pages like `search.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="...">
    <title>Gemini [Tool Name]</title>
    <!-- Apache 2.0 license comment -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="nav.css">
    <style>/* CSS vars + component styles */</style>
</head>
<body>
    <div class="container">
        <nav class="nav"><!-- old nav, hidden by nav.css --></nav>
        <div class="header"><h1>...</h1><p class="subtitle">...</p></div>
        <div class="card">
            <!-- API key + model row -->
            <!-- Tool-specific inputs with presets -->
            <!-- Action button -->
            <!-- Result display -->
            <!-- Error display -->
        </div>
        <div class="footer"><!-- Privacy notice --></div>
    </div>
    <script>/* API logic */</script>
    <script src="nav.js"></script>
</body>
</html>
```

**CSS variables** (copy from search.html): `:root` and `[data-theme="dark"]` blocks with all `--bg`, `--text`, `--accent`, `--border`, etc. vars.

**Common JS pattern** (copy from search.html):
- `API_BASE = 'https://generativelanguage.googleapis.com/v1beta'`
- Theme init: `getPreferredTheme()`, `applyTheme()`, `toggleTheme()`
- `beforeunload` clears API key
- `Ctrl+Enter` or `Enter` keyboard shortcut

---

## Chunk 1: Navigation Update + TTS + Thinking

### Task 1: Update nav.js with all 7 new tools

**Files:**
- Modify: `nav.js:7-28`

- [ ] **Step 1: Add new tools to the sections array in nav.js**

Replace the `sections` array (lines 7-28) with:

```javascript
var sections = [
    { title: 'Analyze', links: [
        ['index.html', 'Token Counter', 'Count tokens in text and images'],
        ['models.html', 'Model Explorer', 'Browse available Gemini models'],
    ]},
    { title: 'Vision', links: [
        ['describe.html', 'Image Describer', 'Describe images with AI'],
        ['detect.html', 'Object Detector', 'Detect objects with bounding boxes'],
        ['video.html', 'Video Analyzer', 'Analyze video content'],
    ]},
    { title: 'Text & Data', links: [
        ['prompt.html', 'Playground', 'Chat with system instructions'],
        ['extract.html', 'Extractor', 'Extract structured data'],
        ['embed.html', 'Embeddings', 'Compute text similarity'],
        ['search.html', 'Search', 'Grounded Google Search'],
        ['pdf.html', 'PDF Analyzer', 'Analyze PDF documents'],
        ['url.html', 'URL Context', 'Summarize and analyze web pages'],
        ['files.html', 'File Search', 'Upload and query documents'],
    ]},
    { title: 'AI Tools', links: [
        ['think.html', 'Thinking', 'See model reasoning step by step'],
        ['code.html', 'Code Runner', 'Generate and execute Python code'],
        ['maps.html', 'Maps', 'Location-aware queries with Google Maps'],
        ['research.html', 'Deep Research', 'Multi-step research agent'],
    ]},
    { title: 'Creative', links: [
        ['tts.html', 'Text to Speech', 'Generate speech from text'],
        ['story.html', 'Story Illustrator', 'Generate illustrated storybooks'],
        ['animate.html', 'Animated Video', 'Create story videos with AI'],
    ]},
];
```

- [ ] **Step 2: Commit**

```bash
git add nav.js
git commit -m "Add 7 new tools to sidebar navigation"
```

---

### Task 2: Create tts.html — Text-to-Speech

**Files:**
- Create: `tts.html`

- [ ] **Step 1: Create tts.html**

CSP needs `media-src blob: data:` for audio playback.

Key UI elements:
- API key + model field (pre-filled: `gemini-2.5-flash-preview-tts`)
- **Voice picker** dropdown with options: Zephyr, Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Perseus
- **Text area** pre-filled with: "Welcome to Gemini Tools! This is a demonstration of text-to-speech. The model can speak naturally, with emotion and expression."
- **Preset buttons**: "Storytelling" (Once upon a time, in a land far away...), "News Anchor" (Breaking news tonight...), "Cheerful Greeting" (Hey there! Great to see you...), "Dramatic Reading" (It was a dark and stormy night...)
- **Generate Speech** button
- Result: `<audio>` element with controls + a Download button
- API call: `POST v1beta/models/{model}:generateContent` with body:

```javascript
{
    contents: [{ parts: [{ text: inputText }] }],
    generationConfig: {
        responseModalities: ["AUDIO"],
        speechConfig: {
            voiceConfig: {
                prebuiltVoiceConfig: {
                    voiceName: selectedVoice
                }
            }
        }
    }
}
```

- Response parsing: `data.candidates[0].content.parts[0].inlineData` contains `{ mimeType, data }`. Convert base64 `data` to audio blob:

```javascript
const audioData = data.candidates[0].content.parts[0].inlineData;
const audioBytes = atob(audioData.data);
const byteArray = new Uint8Array(audioBytes.length);
for (let i = 0; i < audioBytes.length; i++) byteArray[i] = audioBytes.charCodeAt(i);
const blob = new Blob([byteArray], { type: audioData.mimeType });
const audioUrl = URL.createObjectURL(blob);
// Set <audio> src to audioUrl
// Set download link href to audioUrl
```

- [ ] **Step 2: Test in browser**

Open `tts.html`, verify voice picker, presets, and audio playback work.

- [ ] **Step 3: Commit**

```bash
git add tts.html
git commit -m "Add text-to-speech tool with voice picker and audio playback"
```

---

### Task 3: Create think.html — Thinking Mode

**Files:**
- Create: `think.html`

- [ ] **Step 1: Create think.html**

Key UI elements:
- API key + model field (pre-filled: `gemini-2.5-flash`)
- **Thinking budget slider**: range input 0–24576, with labels "Off (0)", "Quick (1024)", "Medium (8192)", "Deep (24576)". Show current value next to slider. Default: 8192.
- **Text area** pre-filled with: "How many r's are in the word 'strawberry'? Explain your reasoning step by step."
- **Preset buttons**: "Math Puzzle" (What is 27 * 43 + 891 / 3?), "Logic Riddle" (A farmer has a fox, chicken and grain...), "Code Debug" (Find the bug: function fib(n) { return fib(n-1) + fib(n-2); }), "Science" (Explain why the sky is blue using Rayleigh scattering)
- **Think** button
- **Two-panel result**:
  - Collapsible "Thought Process" section with `<details><summary>` — styled with muted background, italic text
  - "Final Answer" section — normal styling
  - Token usage display showing thinking tokens vs output tokens

- API call: `POST v1beta/models/{model}:generateContent` with body:

```javascript
{
    contents: [{ parts: [{ text: inputText }] }],
    generationConfig: {
        thinkingConfig: {
            includeThoughts: true,
            thinkingBudget: budgetValue  // from slider
        }
    }
}
```

- Response parsing: iterate `data.candidates[0].content.parts` — parts with `thought: true` go in the thought panel, other text parts go in the answer panel. Show `data.usageMetadata` for token counts.

- [ ] **Step 2: Test in browser**

- [ ] **Step 3: Commit**

```bash
git add think.html
git commit -m "Add thinking mode tool with budget slider and thought display"
```

---

## Chunk 2: Code Execution + URL Context

### Task 4: Create code.html — Code Execution

**Files:**
- Create: `code.html`

- [ ] **Step 1: Create code.html**

Key UI elements:
- API key + model field (pre-filled: `gemini-2.5-flash`)
- **Text area** pre-filled with: "Calculate the first 20 Fibonacci numbers and display them in a formatted table."
- **Preset buttons**: "Fibonacci" (above), "Prime Sieve" (Find all prime numbers under 1000 and show count), "Data Analysis" (Generate sample sales data for 12 months and calculate mean, median, std dev), "Math Proof" (Prove that sqrt(2) is irrational by testing numerical approximations), "String Manipulation" (Write code to check if 'racecar' is a palindrome and explain)
- **Run Code** button
- **Three-section result**:
  - "Explanation" — text parts from response
  - "Generated Code" — `executableCode.code` in a `<pre><code>` block with monospace font, dark background
  - "Output" — `codeExecutionResult.output` in a `<pre>` block with green-tinted background

- API call:

```javascript
{
    contents: [{ parts: [{ text: inputText }] }],
    tools: [{ code_execution: {} }]
}
```

- Response parsing: iterate `data.candidates[0].content.parts`:
  - `part.text` → explanation section
  - `part.executableCode` → code section (use `part.executableCode.code`)
  - `part.codeExecutionResult` → output section (use `part.codeExecutionResult.output`)

- [ ] **Step 2: Test in browser**

- [ ] **Step 3: Commit**

```bash
git add code.html
git commit -m "Add code execution tool with Python code display and output"
```

---

### Task 5: Create url.html — URL Context

**Files:**
- Create: `url.html`

- [ ] **Step 1: Create url.html**

Key UI elements:
- API key + model field (pre-filled: `gemini-2.5-flash`)
- **URL input** pre-filled with: `https://en.wikipedia.org/wiki/Gemini_(language_model)`
- **Question textarea** pre-filled with: "Summarize the key points of this page in bullet points."
- **Preset buttons**: "Summarize" (above), "Extract Facts" (List all factual claims with dates and numbers), "Key People" (Who are the key people or organizations mentioned?), "Timeline" (Create a chronological timeline of events mentioned)
- **Analyze URL** button
- Standard result display with rendered markdown

- API call:

```javascript
{
    contents: [{ parts: [{ text: question + "\n\nURL: " + urlValue }] }],
    tools: [{ url_context: {} }]
}
```

- [ ] **Step 2: Test in browser**

- [ ] **Step 3: Commit**

```bash
git add url.html
git commit -m "Add URL context tool for web page analysis"
```

---

## Chunk 3: Google Maps + Deep Research + File Search

### Task 6: Create maps.html — Google Maps

**Files:**
- Create: `maps.html`

- [ ] **Step 1: Create maps.html**

Key UI elements:
- API key + model field (pre-filled: `gemini-2.5-flash`)
- **Location section**:
  - "Use My Location" button (calls `navigator.geolocation.getCurrentPosition`)
  - City picker dropdown: San Francisco (37.7749, -122.4194), New York (40.7128, -74.0060), London (51.5074, -0.1278), Tokyo (35.6762, 139.6503), Paris (48.8566, 2.3522), Sydney (-33.8688, 151.2093)
  - Display current lat/lng below
- **Question textarea** pre-filled with: "What are the best coffee shops nearby? Include ratings and what they're known for."
- **Preset buttons**: "Coffee Shops" (above), "Restaurants" (What are the top-rated restaurants within walking distance?), "Parks" (What parks or green spaces are nearby for a walk?), "Museums" (What museums or cultural attractions are near here?), "Hotels" (What are the best hotels in this area?)
- **Search** button
- Standard result display

- API call:

```javascript
{
    contents: [{ role: "user", parts: [{ text: question }] }],
    tools: [{ google_maps: {} }],
    toolConfig: {
        retrievalConfig: {
            latLng: {
                latitude: lat,
                longitude: lng
            }
        }
    }
}
```

- [ ] **Step 2: Test in browser**

- [ ] **Step 3: Commit**

```bash
git add maps.html
git commit -m "Add Google Maps grounding tool with geolocation"
```

---

### Task 7: Create research.html — Deep Research

**Files:**
- Create: `research.html`

- [ ] **Step 1: Create research.html**

This is the most complex tool — uses a different API endpoint and polling pattern.

Key UI elements:
- API key field (no model selector — agent name is fixed)
- **Topic textarea** pre-filled with: "What are the latest breakthroughs in quantum computing in 2025? Include key papers, companies, and milestones."
- **Preset buttons**: "Quantum Computing" (above), "AI Safety" (What are the current approaches to AI alignment and safety?), "Climate Tech" (What are the most promising climate technologies being developed?), "Space Exploration" (What are the latest Mars mission developments and findings?)
- **Start Research** button
- **Progress section** (visible during polling):
  - Animated progress indicator (pulsing dot or spinner)
  - Status text: "Researching... This may take 1-5 minutes"
  - Elapsed time counter
- **Result**: Full research report with rendered markdown

- API call — **Create interaction**:

```javascript
const createUrl = API_BASE + '/interactions?key=' + encodeURIComponent(apiKey);
const resp = await fetch(createUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        interactionConfig: {
            responseModality: "RESPONSE_MODALITY_TEXT"
        },
        userInput: {
            parts: [{ text: topic }]
        }
    })
});
const interaction = await resp.json();
const interactionName = interaction.name;
```

- **Poll for completion**:

```javascript
async function pollResearch(interactionName, apiKey) {
    const pollUrl = API_BASE + '/' + interactionName + '?key=' + encodeURIComponent(apiKey);
    while (true) {
        await new Promise(r => setTimeout(r, 5000)); // poll every 5s
        const resp = await fetch(pollUrl);
        const data = await resp.json();
        if (data.done || data.interactionState === 'COMPLETED') {
            return data;
        }
        // Update status text if available
    }
}
```

- Response: Extract the final output text from the completed interaction response.
- **Important**: Show a clear warning that this is a real API call that takes 1-5 minutes and uses significant token quota.

- [ ] **Step 2: Test in browser**

- [ ] **Step 3: Commit**

```bash
git add research.html
git commit -m "Add Deep Research tool with real API polling"
```

---

### Task 8: Create files.html — File Search

**Files:**
- Create: `files.html`

- [ ] **Step 1: Create files.html**

Key UI elements:
- API key + model field (pre-filled: `gemini-2.5-flash`)
- **Drop zone** for file upload (similar to video.html pattern):
  - Accept: `.pdf, .txt, .csv, .html, .json, .xml, .md`
  - Read file as base64 using FileReader
  - Show file name and size after upload
- **Question textarea** pre-filled with: "Summarize the key points in this document."
- **Preset buttons**: "Summarize" (above), "Extract Data" (Extract all tables, numbers and structured data), "Key Findings" (What are the main conclusions or findings?), "Q&A" (What questions does this document answer?)
- **Analyze** button
- Standard result display

- API call — **Two-step process**:

Step 1: Upload file to Files API:
```javascript
const uploadUrl = API_BASE + '/files?key=' + encodeURIComponent(apiKey);
// Use multipart upload with metadata + file content
const metadata = { file: { displayName: fileName } };
const form = new FormData();
// Alternatively, use inline_data for small files (<20MB):
```

For simplicity (matching the video.html pattern), use inline_data for files under 20MB:
```javascript
{
    contents: [{
        parts: [
            { text: question },
            { inline_data: { mime_type: fileMimeType, data: fileBase64 } }
        ]
    }]
}
```

For larger files, use the Files API upload then reference by URI:
```javascript
// Upload
const uploadResp = await fetch(API_BASE + '/files?key=' + apiKey, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file: { displayName: name } })
});
// Then generateContent with file_data part:
{ file_data: { file_uri: uploadedFile.uri, mime_type: uploadedFile.mimeType } }
```

- [ ] **Step 2: Test in browser**

- [ ] **Step 3: Commit**

```bash
git add files.html
git commit -m "Add file search tool with document upload and Q&A"
```

---

## Chunk 4: Final Integration

### Task 9: Update CLAUDE.md with new tools

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the Current Tools list in CLAUDE.md**

Add the 7 new tools to the list.

- [ ] **Step 2: Commit all**

```bash
git add CLAUDE.md
git commit -m "Update CLAUDE.md with new tool list"
```
