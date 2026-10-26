import base64
import json
import urllib.request
import re

SYSTEM_PROMPT = """You are an expert Pokemon competitive battle analyzer. Analyze this Pokemon Champions Team Preview screenshot.
Extract:
1. opponent_name: The trainer name shown in the top-right pink pill/card.
2. format: The battle format (e.g. "Ranked Doubles" or "Ranked Singles").
3. opponent_team: Array of the 6 Pokemon names on the opponent's side (right). Use canonical English names (e.g. "Starmie", "Lucario", "Chandelure", "Indeedee", "Aerodactyl", "Rotom-Wash", "Swampert", "Pelipper", "Farigiraf", "Gholdengo", "Incineroar", "Volcarona").
4. my_team: Array of the 6 Pokemon names on the player's side (left).

Return ONLY a pure JSON object:
{
  "opponent_name": "...",
  "format": "Ranked Doubles",
  "opponent_team": ["...", "...", "...", "...", "...", "..."],
  "my_team": ["...", "...", "...", "...", "...", "..."]
}
"""

def detect_with_gemini(api_key, base64_image):
    # Try gemini-2.5-flash first, fallback to 1.5-flash
    models = ["gemini-2.5-flash", "gemini-1.5-flash"]
    last_err = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"inline_data": {"mime_type": "image/png", "data": base64_image}}
                ]
            }],
            "generationConfig": {"temperature": 0.1, "response_mime_type": "application/json"}
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            last_err = e
            continue
    raise last_err or Exception("Failed to query Gemini API")

def detect_with_ollama(model="moondream", base64_image="", host="http://localhost:11434"):
    url = f"{host}/api/generate"
    payload = {
        "model": model,
        "prompt": SYSTEM_PROMPT + "\nRespond ONLY with the JSON object.",
        "images": [base64_image],
        "stream": False,
        "format": "json"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        raw = data.get("response", "")
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw)
