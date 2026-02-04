# Farm Advisor 🌱

**Offline Agricultural Guidance System**

Farm Advisor is a lightweight, offline-first web app that provides farming guidance in English and Hindi via text and voice. It runs locally (no internet required for core features), supports browser-based speech recognition and synthesis, and includes a searchable knowledge base of agricultural content.

---

## Features ✅

- Offline knowledge base for agricultural guidance (English & Hindi)
- Ask questions by text or voice (browser-based speech recognition)
- Text-to-speech: browser TTS and optional local TTS (pyttsx3)
- Simple interaction history and categories
- Small, self-contained Flask backend and static frontend

---

## Project structure 🔧

- `run.py`, `start.py` - Primary entry scripts to run the app locally
- `requirements.txt` - Python dependencies
- `backend/` - Flask application and backend modules
  - `app.py` - Main Flask app: routes and application logic
  - `models/` - Core modules: `knowledge_base.py`, `speech_handler.py`, `database.py`
  - `data/agricultural_data.json` - Knowledge base (auto-created if missing)
- `frontend/` - Static UI (`index.html`, `static/css`, `static/js`)
- `setup_scripts/` - (placeholders for optional model download or installer scripts)

---

## Installation (Windows / macOS / Linux) 🛠️

1. Clone the repo:

```bash
git clone <your-repo-url>
cd farm-advisor
```

2. Create a virtual environment and activate it:

- Windows (PowerShell):
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

- macOS / Linux (bash):
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

Notes:
- On Windows, `pyaudio` can be tricky to install. If `pip install pyaudio` fails, try `pipwin install pyaudio` or use an appropriate wheel.
- `pyttsx3` is optional (used for local TTS). If not available, browser TTS is used.

---

## Run the app 🏃

Recommended for development:

```bash
python start.py
```

Alternative (production-like) using `run.py` (prints friendly banner and runs server):

```bash
python run.py
```

Open your browser at: http://localhost:5000

For production (example with waitress):

```bash
waitress-serve --port=5000 --call 'app:create_app'
```

---

## API Endpoints 📡

Base: `http://localhost:5000`

- GET `/api/status` - System status
- POST `/api/ask` - Ask a text question
  - Body: `{ "question": "When do I plant rice?", "language": "en" }`
- POST `/api/voice/start` - Start voice recognition (browser-based)
- POST `/api/voice/stop` - Stop voice recognition
- GET `/api/voice/status` - Get voice/listening status
- POST `/api/speak` - Convert server-side text to speech (optional)
  - Body: `{ "text": "Your answer text", "language": "en" }`
- GET `/api/history` - Get recent interactions
- GET `/api/categories` - Get knowledge base categories

Example curl (ask a question):

```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "When should I plant rice?", "language": "en"}'
```

---

## Knowledge Base & Data ✏️

- The knowledge base loads from `backend/data/agricultural_data.json`.
- If the JSON file is missing, the app creates a default knowledge base automatically (see `KnowledgeBase.create_default_knowledge_base`).
- You can extend or replace `agricultural_data.json` with your own categories and entries. Keep the same schema (categories -> entries with `question`, `answer`, and `keywords`).

---

## Speech (Voice) Behavior 🎤

- Speech recognition is handled in the browser (frontend JS) using Web Speech APIs.
- The backend provides optional TTS via `pyttsx3` when available, otherwise browser TTS will be used.
- Supported languages: English (`en`) and Hindi (`hi`)

---

## Troubleshooting & Tips ⚠️

- Port 5000 already in use: stop the other service or change port in `start.py`/`run.py`.
- If TTS fails or is not installed, the app will still work — browser TTS is the default.
- On Windows, if `pyaudio` installation fails, try using `pipwin` or download matching wheel from Christoph Gohlke's site.
- Knowledge base missing or empty: The app auto-creates a default dataset on first run.

---

## Development ✅

- The frontend is in `frontend/` and is served by Flask from `backend/app.py`.
- To add features, edit `backend/models/*` for backend logic and `frontend/static/js/*` for UI behavior.
- There are no automated tests included yet; PRs to add tests are welcome.

---

## Contributing 🤝

Contributions are welcome. Consider these steps:

1. Fork the repository
2. Create a feature branch
3. Add tests / update the knowledge base if relevant
4. Open a pull request describing your changes

---

## License & Attribution 📄

No license file is included in this repository. Add a `LICENSE` file (for example MIT) if you want to permit reuse. If you want, add one and update this README accordingly.

---

## Contact / Author

Project created as **Farm Advisor** — an offline-first toolkit for delivering agricultural guidance via a simple local web interface.

If you want help adding features (e.g., Vosk offline speech, additional languages, or model downloads), open an issue or a PR with your ideas.

---

Thank you for using Farm Advisor! 🌾
