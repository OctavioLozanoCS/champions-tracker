import base64
import json
import urllib.request
import re
import os
import regulations

POKEMON_LIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "pokemon_list.json")
_CANONICAL_MAP = None

def _load_canonical_map():
    global _CANONICAL_MAP
    if _CANONICAL_MAP is not None:
        return _CANONICAL_MAP
    _CANONICAL_MAP = {}
    if os.path.exists(POKEMON_LIST_PATH):
        try:
            with open(POKEMON_LIST_PATH, "r", encoding="utf-8") as f:
                names = json.load(f)
                for name in names:
                    _CANONICAL_MAP[name.lower()] = name
                    _CANONICAL_MAP[name.lower().replace("-", " ")] = name
                    _CANONICAL_MAP[name.lower().replace(" ", "-")] = name
        except Exception:
            pass
    return _CANONICAL_MAP

# Aliases and common misidentifications
ALIASES = {
    "sneasler": "Sneasler",
    "sneasel": "Sneasel",
    "sneasel-hisui": "Hisuian Sneasel",
    "hisuian sneasel": "Hisuian Sneasel",
    "basculegion": "Basculegion",
    "basculegion-m": "Basculegion-Male",
    "basculegion m": "Basculegion-Male",
    "basculegion-male": "Basculegion-Male",
    "basculegion male": "Basculegion Male",
    "basculegion (male)": "Basculegion-Male",
    "basculegion-f": "Basculegion-Female",
    "basculegion f": "Basculegion-Female",
    "basculegion-female": "Basculegion-Female",
    "basculegion female": "Basculegion Female",
    "basculegion (female)": "Basculegion-Female",
    "urshifu-r": "Urshifu-Rapid-Strike",
    "urshifu rapid": "Urshifu-Rapid-Strike",
    "urshifu rapid strike": "Urshifu-Rapid-Strike",
    "urshifu-rapid-strike": "Urshifu-Rapid-Strike",
    "urshifu-s": "Urshifu-Single-Strike",
    "urshifu single": "Urshifu-Single-Strike",
    "urshifu single strike": "Urshifu-Single-Strike",
    "urshifu-single-strike": "Urshifu-Single-Strike",
    "indeedee-f": "Indeedee-Female",
    "indeedee female": "Indeedee-Female",
    "indeedee (f)": "Indeedee-Female",
    "indeedee-m": "Indeedee-Male",
    "indeedee male": "Indeedee-Male",
    "indeedee (m)": "Indeedee-Male",
    "bloodmoon": "Ursaluna-Bloodmoon",
    "bloodmoon ursaluna": "Ursaluna-Bloodmoon",
    "ursaluna bloodmoon": "Ursaluna-Bloodmoon",
    "ursaluna-bloodmoon": "Ursaluna-Bloodmoon",
    "ogerpon-w": "Ogerpon-Wellspring",
    "ogerpon wellspring": "Ogerpon-Wellspring",
    "ogerpon-h": "Ogerpon-Hearthflame",
    "ogerpon hearthflame": "Ogerpon-Hearthflame",
    "ogerpon-c": "Ogerpon-Cornerstone",
    "ogerpon cornerstone": "Ogerpon-Cornerstone",
    "ogerpon-t": "Ogerpon-Teal",
    "ogerpon teal": "Ogerpon-Teal",
    "calyrex-s": "Calyrex-Shadow",
    "calyrex shadow": "Calyrex-Shadow",
    "calyrex shadow rider": "Calyrex-Shadow",
    "calyrex-i": "Calyrex-Ice",
    "calyrex ice": "Calyrex-Ice",
    "calyrex ice rider": "Calyrex-Ice",
    "landorus-t": "Landorus-Therian",
    "landorus therian": "Landorus-Therian",
    "tornadus-t": "Tornadus-Therian",
    "tornadus therian": "Tornadus-Therian",
    "thundurus-t": "Thundurus-Therian",
    "thundurus therian": "Thundurus-Therian",
    "enamorus-t": "Enamorus-Therian",
    "enamorus therian": "Enamorus-Therian",
    "rotom-w": "Rotom-Wash",
    "rotom wash": "Rotom-Wash",
    "rotom-h": "Rotom-Heat",
    "rotom heat": "Rotom-Heat",
    "rotom-f": "Rotom-Frost",
    "rotom frost": "Rotom-Frost",
    "rotom-c": "Rotom-Mow",
    "rotom mow": "Rotom-Mow",
    "rotom-s": "Rotom-Fan",
    "rotom fan": "Rotom-Fan",
    "chien pao": "Chien-Pao",
    "ting lu": "Ting-Lu",
    "wo chien": "Wo-Chien",
    "chi yu": "Chi-Yu",
    "ho oh": "Ho-Oh",
    "porygon z": "Porygon-Z",
    "type null": "Type: Null",
    "jangmo o": "Jangmo-o",
    "hakamo o": "Hakamo-o",
    "kommo o": "Kommo-o",
    # Pokémon Champions & Regulation M-C Megas
    "mega garchomp z": "Mega Garchomp Z",
    "garchomp z": "Mega Garchomp Z",
    "garchomp-z": "Mega Garchomp Z",
    "mega lucario z": "Mega Lucario Z",
    "lucario z": "Mega Lucario Z",
    "lucario-z": "Mega Lucario Z",
    "mega absol z": "Mega Absol Z",
    "absol z": "Mega Absol Z",
    "absol-z": "Mega Absol Z",
    "mega baxcalibur": "Mega Baxcalibur",
    "baxcalibur mega": "Mega Baxcalibur",
    "mega golisopod": "Mega Golisopod",
    "golisopod mega": "Mega Golisopod",
    "mega salamence": "Mega Salamence",
    "salamence mega": "Mega Salamence",
    "mega dragonite": "Mega Dragonite",
    "dragonite mega": "Mega Dragonite",
    "mega raichu x": "Mega Raichu X",
    "raichu mega x": "Mega Raichu X",
    "mega raichu y": "Mega Raichu Y",
    "raichu mega y": "Mega Raichu Y",
    "mega metagross": "Mega Metagross",
    "metagross mega": "Mega Metagross",
}

def normalize_pokemon_name(name):
    if not name or not isinstance(name, str):
        return ""
    clean = name.strip()
    clean_lower = clean.lower()

    if clean_lower in ALIASES:
        return ALIASES[clean_lower]

    cmap = _load_canonical_map()
    if clean_lower in cmap:
        return cmap[clean_lower]
    
    m = re.match(r"^(.+?)\s*\((.+?)\)$", clean)
    if m:
        base, form = m.group(1).strip(), m.group(2).strip()
        candidate = f"{base}-{form}"
        if candidate.lower() in ALIASES:
            return ALIASES[candidate.lower()]
        if candidate.lower() in cmap:
            return cmap[candidate.lower()]

    parts = re.split(r"([ -])", clean)
    formatted = "".join(
        p.capitalize() if p not in ["-", " "] else p
        for p in parts
    )
    return formatted

def build_system_prompt(regulation="Regulation M-C"):
    reg_rules = regulations.get_regulation_ai_prompt(regulation)
    return f"""You are an expert Pokemon competitive battle analyzer. Analyze this Pokemon Champions Team Preview screenshot.
Extract:
1. opponent_name: The trainer name shown in the top-right pink pill/card.
2. format: The battle format (e.g. "Ranked Doubles" or "Ranked Singles").
3. opponent_team: Array of the 6 Pokemon names on the opponent's side (right).
4. my_team: Array of the 6 Pokemon names on the player's side (left).

BATTLE REGULATION ENFORCEMENT:
Active Regulation: {regulation}
Rules & Permitted Pool:
{reg_rules}
You MUST strictly restrict your detected Pokemon choices to those permitted under {regulation}. Do not hallucinate or return banned Pokemon.

Critical Disambiguation & Canonical Naming Rules:
- Mega Evolutions: If a Pokemon is Mega Evolved or in Mega form, specify with 'Mega ' prefix (e.g. 'Mega Garchomp Z', 'Mega Lucario Z', 'Mega Baxcalibur', 'Mega Golisopod', 'Mega Salamence', 'Mega Charizard Y', 'Mega Kangaskhan', 'Mega Gengar', 'Mega Dragonite', 'Mega Raichu X') or detect base form.
- Sneasler vs Sneasel/Weavile: Sneasler is tall and slender with long limbs, grey/purple body, and a long magenta head feather. Do NOT mislabel Sneasler as Sneasel or Weavile.
- Basculegion vs Basculin: Basculegion is a large ghostly fish. Distinguish Basculegion-Male (reddish/pink ghostly spirit tails) vs Basculegion-Female (cyan/light blue ghostly spirit tails).
- Urshifu: Identify "Urshifu-Rapid-Strike" (blue accents, flowing water) vs "Urshifu-Single-Strike" (red accents, dark stance).
- Indeedee: Identify "Indeedee-Female" (white head, brown facial patterns) vs "Indeedee-Male" (dark blue face).
- Ursaluna vs Ursaluna-Bloodmoon: Ursaluna-Bloodmoon has the dark reddish round moon crest on forehead.
- Ogerpon: Specify mask if visible: "Ogerpon-Wellspring", "Ogerpon-Hearthflame", "Ogerpon-Cornerstone", or "Ogerpon-Teal".
- Calyrex: Specify "Calyrex-Shadow" (riding Spectrier) or "Calyrex-Ice" (riding Glastrier).
- Forces of Nature: Use "Landorus-Therian", "Tornadus-Therian", "Thundurus-Therian", etc.
- Rotom: Use "Rotom-Wash", "Rotom-Heat", "Rotom-Frost", "Rotom-Mow", "Rotom-Fan".
- Use canonical English names (e.g., "Gholdengo", "Kingambit", "Flutter Mane", "Incineroar", "Sinistcha", "Farigiraf", "Archaludon", "Chien-Pao").

Return ONLY a pure JSON object:
{{
  "opponent_name": "...",
  "format": "Ranked Doubles",
  "opponent_team": ["...", "...", "...", "...", "...", "..."],
  "my_team": ["...", "...", "...", "...", "...", "..."]
}}
"""

def _clean_detection_result(data, regulation="Regulation M-C"):
    if not isinstance(data, dict):
        return data
    if "opponent_team" in data and isinstance(data["opponent_team"], list):
        data["opponent_team"] = [normalize_pokemon_name(p) for p in data["opponent_team"] if p]
    if "my_team" in data and isinstance(data["my_team"], list):
        data["my_team"] = [normalize_pokemon_name(p) for p in data["my_team"] if p]
    return data

def detect_with_gemini(api_key, base64_image, regulation="Regulation M-C"):
    models = ["gemini-2.5-flash", "gemini-1.5-flash"]
    last_err = None
    prompt = build_system_prompt(regulation)
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
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
                return _clean_detection_result(json.loads(text), regulation)
        except Exception as e:
            last_err = e
            continue
    raise last_err or Exception("Failed to query Gemini API")

def detect_with_ollama(model="moondream", base64_image="", host="http://localhost:11434", regulation="Regulation M-C"):
    url = f"{host}/api/generate"
    prompt = build_system_prompt(regulation)
    payload = {
        "model": model,
        "prompt": prompt + "\nRespond ONLY with the JSON object.",
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
            return _clean_detection_result(json.loads(match.group(0)), regulation)
        return _clean_detection_result(json.loads(raw), regulation)
