# Token Counter App (Gemini Tools)

## Project Structure
- Static HTML app — each tool is a standalone `.html` file (no build system, no framework)
- Shared nav via `nav.css` and `nav.js` linked in each page
- All pages use DM Sans font, CSS custom properties for theming (light/dark)
- API calls go directly to `https://generativelanguage.googleapis.com/v1beta`

## Conventions
- Each page is self-contained: HTML + inline `<style>` + inline `<script>`
- API key persisted in sessionStorage (shared across pages in same tab, cleared on tab close)
- API key load/save logic centralized in nav.js — individual pages should NOT manage key persistence
- CSP meta tag on each page restricts sources
- Nav links listed in every page's `<nav>` — update all pages when adding a new tool
- Design: minimal, card-based layout with var(--accent) indigo theme

## Current Tools
index.html (Home), tokens.html (Token Counter), models.html, describe.html, embed.html,
extract.html, prompt.html (Playground), search.html, detect.html (3D Spatial),
pdf.html, video.html, animate.html, story.html, tts.html (Text-to-Speech),
think.html (Thinking), code.html (Code Runner), url.html (URL Context),
maps.html (Maps), research.html (Deep Research), files.html (File Search),
live.html (Live Chat), cache.html (Context Cache)

## Nav Structure (nav.js)
- Analyze: Token Counter, Model Explorer
- Vision: Image Describer, 3D Spatial, Video Analyzer
- Text & Data: Playground, Extractor, Embeddings, Search, PDF, URL Context, File Search
- AI Tools: Thinking, Code Runner, Maps, Deep Research, Live Chat, Context Cache
- Creative: Text to Speech, Story Illustrator, AI Video Generator (Veo)

## UX Principle
- Pre-populate everything, use toggles/presets, minimize user input
- Users should see capabilities without having to think or configure

## Workflow (MANDATORY)
- **ALWAYS commit AND push changes to GitHub** — every commit must be followed by `git push`. No exceptions.
- Never leave committed changes unpushed. The task is not done until changes are on the remote.
