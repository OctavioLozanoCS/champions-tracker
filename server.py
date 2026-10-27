import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import base64
from datetime import datetime

from db import (
    init_db, add_match, get_matches, delete_match, update_match, get_stats,
    get_sessions, create_session, set_active_session, clear_session_matches, delete_session, get_active_session_id,
    update_session_regulation
)
import auto_detector
import regulations

PORT = 5050
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
MATCHES_DIR = os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\Octav"), "Desktop", "Matches")
ROSTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "roster.json")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "config.json")

def load_roster():
    if os.path.exists(ROSTER_FILE):
        try:
            with open(ROSTER_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return ["Floette", "Garchomp", "Incineroar", "Sinistcha", "Sneasler", "Kingambit"]

def save_roster(roster):
    os.makedirs(os.path.dirname(ROSTER_FILE), exist_ok=True)
    with open(ROSTER_FILE, "w") as f:
        json.dump(roster, f, indent=2)

def load_config():
    default_cfg = {
        "provider": "gemini",
        "gemini_api_key": "",
        "ollama_host": "http://localhost:11434",
        "ollama_model": "moondream",
        "auto_detect_on_snap": True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                default_cfg.update(data)
                return default_cfg
        except Exception:
            pass
    return default_cfg

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

class TrackerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw = self.rfile.read(content_length)
            return json.loads(raw.decode("utf-8"))
        return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/stats":
            fmt = query.get("format", [None])[0]
            session_id = query.get("session_id", [None])[0]
            stats = get_stats(format_filter=fmt, session_id=session_id)
            self._send_json(stats)
            return

        elif path == "/api/matches":
            fmt = query.get("format", [None])[0]
            session_id = query.get("session_id", [None])[0]
            limit = int(query.get("limit", [100])[0])
            matches = get_matches(limit=limit, format_filter=fmt, session_id=session_id)
            self._send_json(matches)
            return

        elif path == "/api/sessions":
            self._send_json({
                "sessions": get_sessions(),
                "active_id": get_active_session_id()
            })
            return

        elif path == "/api/regulations":
            self._send_json(regulations.get_available_regulations())
            return

        elif path == "/api/regulations/pokemon":
            reg = query.get("regulation", ["All / Open"])[0]
            self._send_json(regulations.get_legal_pokemon_for_regulation(reg))
            return

        elif path == "/api/export":
            session_id = query.get("session_id", [None])[0]
            matches = get_matches(limit=10000, session_id=session_id)
            self._send_json(matches)
            return

        elif path == "/api/roster":
            self._send_json(load_roster())
            return

        elif path == "/api/config":
            self._send_json(load_config())
            return

        # Fallback to static files
        if path == "/" or path == "":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/matches":
            try:
                data = self._read_json()
                match_id = add_match(
                    result=data.get("result", "WIN"),
                    my_team=data.get("my_team", []),
                    opp_team=data.get("opp_team", []),
                    format=data.get("format", "Ranked Doubles"),
                    tier=data.get("tier", ""),
                    opponent_name=data.get("opponent_name", ""),
                    score=data.get("score", ""),
                    notes=data.get("notes", ""),
                    mvp=data.get("mvp", ""),
                    my_mega=data.get("my_mega", ""),
                    opp_mega=data.get("opp_mega", ""),
                    source=data.get("source", "manual"),
                    session_id=data.get("session_id")
                )
                self._send_json({"success": True, "id": match_id, "stats": get_stats()})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        elif path == "/api/sessions":
            try:
                data = self._read_json()
                name = data.get("name", "").strip()
                reg = data.get("regulation", "All / Open")
                s_id = create_session(name, regulation=reg)
                self._send_json({"success": True, "id": s_id, "sessions": get_sessions()})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        elif path == "/api/sessions/active":
            try:
                data = self._read_json()
                s_id = int(data.get("id"))
                set_active_session(s_id)
                self._send_json({"success": True, "active_id": s_id, "sessions": get_sessions()})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        elif path == "/api/sessions/regulation":
            try:
                data = self._read_json()
                s_id = int(data.get("id"))
                reg = data.get("regulation", "All / Open")
                update_session_regulation(s_id, reg)
                self._send_json({"success": True, "sessions": get_sessions()})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        elif path == "/api/sessions/clear":
            try:
                data = self._read_json()
                s_id = int(data.get("id"))
                cleared = clear_session_matches(s_id)
                self._send_json({"success": True, "cleared": cleared, "sessions": get_sessions()})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        elif path == "/api/roster":
            try:
                data = self._read_json()
                if isinstance(data, list):
                    save_roster(data)
                    self._send_json({"success": True, "roster": data})
                else:
                    self._send_json({"error": "Expected a list of Pokemon names"}, status=400)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        elif path == "/api/config":
            try:
                data = self._read_json()
                current = load_config()
                current.update(data)
                save_config(current)
                self._send_json({"success": True, "config": current})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        elif path == "/api/save-screenshot":
            try:
                data = self._read_json()
                img_data = data.get("image", "")
                if "," in img_data:
                    img_data = img_data.split(",", 1)[1]
                
                os.makedirs(MATCHES_DIR, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Match_{timestamp}.png"
                filepath = os.path.join(MATCHES_DIR, filename)

                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(img_data))

                print(f"[SCREENSHOT SAVED]: {filepath}")
                self._send_json({
                    "success": True,
                    "filename": filename,
                    "filepath": filepath,
                    "relative_url": f"/Matches/{filename}"
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        elif path == "/api/auto-detect":
            try:
                data = self._read_json()
                img_data = data.get("image", "")
                reg = data.get("regulation", "All / Open")
                if "," in img_data:
                    img_data = img_data.split(",", 1)[1]

                cfg = load_config()
                provider = cfg.get("provider", "gemini")
                api_key = cfg.get("gemini_api_key", "").strip()
                ollama_host = cfg.get("ollama_host", "http://localhost:11434")
                ollama_model = cfg.get("ollama_model", "moondream")

                if provider == "gemini":
                    if not api_key:
                        self._send_json({
                            "success": False,
                            "configured": False,
                            "message": "Gemini API key is not configured. Enter your free API key in Settings."
                        })
                        return
                    detected = auto_detector.detect_with_gemini(api_key, img_data, regulation=reg)
                    self._send_json({"success": True, "configured": True, "data": detected})
                    return

                elif provider == "ollama":
                    try:
                        detected = auto_detector.detect_with_ollama(model=ollama_model, base64_image=img_data, host=ollama_host, regulation=reg)
                        self._send_json({"success": True, "configured": True, "data": detected})
                        return
                    except Exception as oe:
                        self._send_json({
                            "success": False,
                            "configured": True,
                            "message": f"Could not reach Ollama at {ollama_host}: {str(oe)}"
                        })
                        return

                self._send_json({"success": False, "message": "Unknown provider configured."})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status=500)
            return

        elif path == "/api/import":
            try:
                data = self._read_json()
                count = 0
                for item in data:
                    add_match(
                        result=item.get("result", "WIN"),
                        my_team=item.get("my_team", []),
                        opp_team=item.get("opp_team", []),
                        format=item.get("format", "Ranked Doubles"),
                        tier=item.get("tier", ""),
                        opponent_name=item.get("opponent_name", ""),
                        score=item.get("score", ""),
                        notes=item.get("notes", ""),
                        mvp=item.get("mvp", ""),
                        my_mega=item.get("my_mega", ""),
                        opp_mega=item.get("opp_mega", ""),
                        source=item.get("source", "import"),
                        session_id=item.get("session_id"),
                        created_at=item.get("created_at")
                    )
                    count += 1
                self._send_json({"success": True, "imported": count, "stats": get_stats()})
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        self._send_json({"error": "Not found"}, status=404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        
        # /api/matches/<id>
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "matches":
            try:
                match_id = int(parts[2])
                success = delete_match(match_id)
                self._send_json({"success": success, "stats": get_stats()})
                return
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
                return

        # /api/sessions/<id>
        elif len(parts) == 3 and parts[0] == "api" and parts[1] == "sessions":
            try:
                s_id = int(parts[2])
                delete_session(s_id)
                self._send_json({"success": True, "sessions": get_sessions()})
                return
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
                return

        self._send_json({"error": "Not found"}, status=404)

def run():
    init_db()
    with socketserver.TCPServer(("", PORT), TrackerHandler) as httpd:
        print(f"======================================================")
        print(f"  POKEMON CHAMPIONS MATCHUP TRACKER")
        print(f"  Running at: http://localhost:{PORT}")
        print(f"======================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    run()
