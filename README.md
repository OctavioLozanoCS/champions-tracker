# 🏆 Pokémon Champions Matchup & Battle Intelligence Tracker

A dedicated, lightweight battle tracking and matchup analytics dashboard designed for **Pokémon Champions** (VGC Ranked Doubles, Ranked Singles, and Casual).

Features zero third-party pip dependencies, instant in-app screen capture, AI vision auto-detection (Gemini Flash or local Ollama), session tracking, threat matrix analytics, and fast 2-letter autocomplete.

---

## 🚀 Quick Start

1. **Launch**: Double-click **`start.bat`** (or run `python server.py`).
2. **Access**: It will automatically launch and open your browser at:
   **[http://localhost:5050](http://localhost:5050)**

---

## ⚡ Instant Game Capture & AI Auto-Detection

### 1. Two-Step In-App Screen Logging
1. Click **`🔗 Select Game Window`** in the dashboard header:
   - Select your Pokémon Champions game window, capture card feed, or OBS projector.
   - The stream stays bound in the background.
2. At Team Preview (or after battle), click **`⚡ SNAP SCREENSHOT`** (or press **`F8`**):
   - Instantly captures the active frame without opening any popups.
   - Saves a timestamped screenshot directly to `Matches/Match_<timestamp>.png`.
   - **Auto-Detection**: The vision engine analyzes the 3D models and preview screen to auto-fill:
     - Opponent Trainer Name (e.g., *Shonos*, *arazo*)
     - Opponent's 6 Pokémon (e.g., *Starmie, Lucario, Chandelure, Indeedee, Aerodactyl, Rotom-Wash*)
     - Battle format & tier
   - Click your 4 brought Pokémon using the 1-click roster chips, select **WIN** or **LOSS**, and hit Save!

---

## 🧠 Vision & Auto-Detection Options (⚙️ Settings)

Open **⚙️ Settings** in the top navigation bar to choose your detection mode:

- **Google Gemini Flash (Recommended / Free)**:
  - Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).
  - Paste it into Settings $\rightarrow$ high-accuracy multi-Pokémon identification in ~1.5s with zero local GPU load.
- **Local Ollama (100% Offline / Zero Tokens)**:
  - Run [Ollama](https://ollama.com) with a vision model: `ollama run moondream` (or `llava`).
  - Set host to `http://localhost:11434` $\rightarrow$ completely local, zero tokens, zero internet required.
- **Smart 2-Letter Fast Autocomplete**:
  - Don't want AI? Just type 2 letters into the Pokémon box (e.g., `sw` $\rightarrow$ Swampert, `pel` $\rightarrow$ Pelipper, `gh` $\rightarrow$ Gholdengo) and press Enter. Backed by a full 1,100+ canonical Pokémon database.

---

## 📂 Sessions & Tournament Runs

- **Session Switching**: Organize matches by ranked sessions, tournaments, practice blocks, or team variations.
- **`+ New Session`**: Archive previous stats and start fresh on a new slate with 0W - 0L.
- **Session Manager**: View historical win rates for each session, rename, clear matches, or switch active sessions.

---

## 📊 Analytics & Threat Intelligence

- **Threat Matchup Matrix**: Automatically computes your win rate and record against every opponent Pokémon you face.
- **My Team Performance**: Tracks win rates, pick rates, and records for each member of your team.
- **1-Click Roster Selector**: Customize your active 6-Pokémon roster in Settings to log your team in 2 seconds.
- **Search & Filter**: Search battle history by opponent name, Pokémon, or notes.
- **Backup & Export**: One-click JSON backup export of your complete match history.

---

## 🛠️ Architecture & Requirements

- **Backend**: Python 3 standard library (`http.server`, `sqlite3`, `json`, `urllib`). **No pip install required!**
- **Frontend**: Vanilla HTML5, CSS3 (responsive dark modern theme), and modern ES6 JavaScript.
- **Database**: SQLite3 (`data/matches.db`), auto-initialized on first run.
