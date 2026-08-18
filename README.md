# AI Playground 0

A single-page web application that demonstrates generative AI capabilities — text chat and image generation — powered by Google Gemini 2.0 Flash. Built as a learning project during NTU's "Developing Intelligent Applications with GPT API" course (March 2024).

## What It Does

1. **Text Generator** — Chat with Gemini 2.0 Flash (free tier)
2. **Image Generator** — Create images via Gemini's native image generation model
3. **History** — Saves your queries and responses locally in your browser

## Architecture

```
ai-playground-0/
├── api/
│   └── index.py          # Vercel serverless function (Python backend)
├── public/
│   ├── index.html        # Single-page frontend
│   ├── style.css         # Bugatti design system styling
│   └── app.js            # Frontend logic (fetch API calls)
├── vercel.json           # Vercel config (routing + build)
├── requirements.txt      # Python deps
└── .env.example          # Placeholder for GEMINI_API_KEY
```

## Tech Stack

- **Frontend:** Vanilla HTML/CSS/JS, Bugatti design system styling (monochrome luxury aesthetic)
- **Backend:** Vercel serverless Python function (`@vercel/python`)
- **AI:** Google Gemini 2.0 Flash (text + image generation via `google-genai` SDK)

## Setup

### 1. Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key" (free tier: 1,500 requests/day, 15 RPM)
3. Copy the key

### 2. Deploy to Vercel

#### Via Composio MCP (recommended)

If your AI assistant has Composio MCP with the Vercel toolkit:

1. Ensure your Vercel connection is active
2. Have the assistant run the provisioning flow:
   - Create project `ai-playground-0`
   - Set framework to `none` (static + serverless)
   - Add env var `GEMINI_API_KEY` with your real key
   - Deploy

#### Manually

1. Push this repo to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import the repo
4. Framework: **Other** (Vite not needed — `vercel.json` handles routing)
5. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: your Google AI Studio key
   - Targets: Production, Preview, Development
6. Click Deploy

### 3. Local Dev (optional)

```bash
pip install -r requirements.txt
# Create .env with your GEMINI_API_KEY
python -m api.index  # or use vercel dev
```

## Design System

Styled after [Bugatti](https://getdesign.md/bugatti) — pure black canvas, white uppercase display type (Saira Condensed), serif body text (EB Garamond), monospace accents (JetBrains Mono). Transparent pill buttons, no border-radius, no accent color except a desaturated ice-blue for links.

## Credits

- Built by [gelwuyl](https://github.com/gelwuyl)
- Originally created during NTU PACE course "Developing Intelligent Applications with GPT API" (March 2024)
- Migrated from Flask/Replit to Vercel/Gemini in August 2026
