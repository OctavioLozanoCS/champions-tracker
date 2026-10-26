import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "matches.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        # Create sessions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active'
            )
        """)

        # Create matches table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                result TEXT NOT NULL,
                format TEXT NOT NULL DEFAULT 'Ranked Doubles',
                tier TEXT DEFAULT '',
                opponent_name TEXT DEFAULT '',
                my_team TEXT NOT NULL,
                opp_team TEXT NOT NULL,
                score TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                mvp TEXT DEFAULT '',
                source TEXT DEFAULT 'manual',
                session_id INTEGER DEFAULT 1
            )
        """)

        # Migration: ensure session_id column exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(matches)")
        cols = [row["name"] for row in cursor.fetchall()]
        if "session_id" not in cols:
            conn.execute("ALTER TABLE matches ADD COLUMN session_id INTEGER DEFAULT 1")

        # Ensure default session exists
        cursor.execute("SELECT COUNT(*) as cnt FROM sessions")
        if cursor.fetchone()["cnt"] == 0:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO sessions (name, created_at, status) VALUES (?, ?, ?)", ("Session 1", now_str, "active"))
            conn.execute("UPDATE matches SET session_id = 1 WHERE session_id IS NULL OR session_id = 0")

        conn.commit()

def get_active_session_id():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sessions WHERE status = 'active' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row["id"]
        # Fallback to most recent session
        cursor.execute("SELECT id FROM sessions ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row["id"]
        # Create one if none
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO sessions (name, created_at, status) VALUES (?, ?, ?)", ("Session 1", now_str, "active"))
        conn.commit()
        return cursor.lastrowid

def set_active_session(session_id):
    with get_connection() as conn:
        conn.execute("UPDATE sessions SET status = 'archived' WHERE id != ?", (session_id,))
        conn.execute("UPDATE sessions SET status = 'active' WHERE id = ?", (session_id,))
        conn.commit()
        return True

def get_sessions():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY id DESC")
        rows = cursor.fetchall()
        
        sessions = []
        for r in rows:
            s = dict(r)
            s_id = s["id"]
            # Get stats for this session
            cursor.execute("SELECT result, COUNT(*) as cnt FROM matches WHERE session_id = ? GROUP BY result", (s_id,))
            res_rows = cursor.fetchall()
            wins = sum(x["cnt"] for x in res_rows if x["result"] == "WIN")
            losses = sum(x["cnt"] for x in res_rows if x["result"] == "LOSS")
            total = sum(x["cnt"] for x in res_rows)
            win_rate = round((wins / total * 100), 1) if total > 0 else 0.0
            
            s["total"] = total
            s["wins"] = wins
            s["losses"] = losses
            s["win_rate"] = win_rate
            sessions.append(s)
        return sessions

def create_session(name, set_active=True):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        if set_active:
            conn.execute("UPDATE sessions SET status = 'archived'")
        cursor.execute("INSERT INTO sessions (name, created_at, status) VALUES (?, ?, ?)", 
                       (name.strip() or f"Session {datetime.now().strftime('%b %d')}", now_str, 'active' if set_active else 'archived'))
        conn.commit()
        return cursor.lastrowid

def clear_session_matches(session_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches WHERE session_id = ?", (session_id,))
        conn.commit()
        return cursor.rowcount

def delete_session(session_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        # If deleted active, make latest active
        get_active_session_id()
        return True

def clean_team_list(team):
    if isinstance(team, str):
        try:
            parsed = json.loads(team)
            if isinstance(parsed, list):
                return [p.strip() for p in parsed if p.strip()]
        except Exception:
            return [p.strip() for p in team.split(",") if p.strip()]
    elif isinstance(team, list):
        return [str(p).strip() for p in team if str(p).strip()]
    return []

def add_match(result, my_team, opp_team, format="Ranked Doubles", tier="", opponent_name="", score="", notes="", mvp="", source="manual", session_id=None, created_at=None):
    if not created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if session_id is None:
        session_id = get_active_session_id()

    my_team_clean = clean_team_list(my_team)
    opp_team_clean = clean_team_list(opp_team)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO matches (created_at, result, format, tier, opponent_name, my_team, opp_team, score, notes, mvp, source, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            created_at,
            result.upper().strip(),
            format.strip(),
            tier.strip(),
            opponent_name.strip(),
            json.dumps(my_team_clean),
            json.dumps(opp_team_clean),
            score.strip(),
            notes.strip(),
            mvp.strip(),
            source.strip(),
            session_id
        ))
        conn.commit()
        return cursor.lastrowid

def get_matches(limit=100, format_filter=None, session_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM matches"
        conditions = []
        params = []
        
        if format_filter and format_filter != "all":
            conditions.append("format = ?")
            params.append(format_filter)
            
        if session_id is not None and str(session_id) != "all":
            conditions.append("session_id = ?")
            params.append(int(session_id))

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        matches = []
        for r in rows:
            m = dict(r)
            m["my_team"] = json.loads(m["my_team"]) if m["my_team"] else []
            m["opp_team"] = json.loads(m["opp_team"]) if m["opp_team"] else []
            matches.append(m)
        return matches

def delete_match(match_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches WHERE id = ?", (match_id,))
        conn.commit()
        return cursor.rowcount > 0

def update_match(match_id, **fields):
    allowed = ["result", "format", "tier", "opponent_name", "my_team", "opp_team", "score", "notes", "mvp", "session_id"]
    updates = []
    params = []
    for k, v in fields.items():
        if k in allowed:
            if k in ["my_team", "opp_team"]:
                v = json.dumps(clean_team_list(v))
            elif k == "result":
                v = v.upper().strip()
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return False
    params.append(match_id)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE matches SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        return cursor.rowcount > 0

def get_stats(format_filter=None, session_id=None):
    matches = get_matches(limit=1000, format_filter=format_filter, session_id=session_id)
    total = len(matches)
    wins = sum(1 for m in matches if m["result"] == "WIN")
    losses = sum(1 for m in matches if m["result"] == "LOSS")
    draws = sum(1 for m in matches if m["result"] == "DRAW")
    win_rate = round((wins / total * 100), 1) if total > 0 else 0.0

    # Calculate streak
    streak_count = 0
    streak_type = None
    for m in matches:
        res = m["result"]
        if res not in ["WIN", "LOSS"]:
            continue
        if streak_type is None:
            streak_type = res
            streak_count = 1
        elif streak_type == res:
            streak_count += 1
        else:
            break

    # Matchup against opponent Pokémon
    opp_pokemon_stats = {}
    for m in matches:
        res = m["result"]
        for p in m["opp_team"]:
            p_name = p.title()
            if p_name not in opp_pokemon_stats:
                opp_pokemon_stats[p_name] = {"pokemon": p_name, "wins": 0, "losses": 0, "total": 0, "win_rate": 0.0}
            opp_pokemon_stats[p_name]["total"] += 1
            if res == "WIN":
                opp_pokemon_stats[p_name]["wins"] += 1
            elif res == "LOSS":
                opp_pokemon_stats[p_name]["losses"] += 1

    for p_name, data in opp_pokemon_stats.items():
        if data["total"] > 0:
            data["win_rate"] = round((data["wins"] / data["total"]) * 100, 1)

    opp_matchups = sorted(opp_pokemon_stats.values(), key=lambda x: (x["total"], x["win_rate"]), reverse=True)

    # My Pokémon Performance
    my_pokemon_stats = {}
    for m in matches:
        res = m["result"]
        for p in m["my_team"]:
            p_name = p.title()
            if p_name not in my_pokemon_stats:
                my_pokemon_stats[p_name] = {"pokemon": p_name, "wins": 0, "losses": 0, "total": 0, "win_rate": 0.0}
            my_pokemon_stats[p_name]["total"] += 1
            if res == "WIN":
                my_pokemon_stats[p_name]["wins"] += 1
            elif res == "LOSS":
                my_pokemon_stats[p_name]["losses"] += 1

    for p_name, data in my_pokemon_stats.items():
        if data["total"] > 0:
            data["win_rate"] = round((data["wins"] / data["total"]) * 100, 1)

    my_performance = sorted(my_pokemon_stats.values(), key=lambda x: (x["total"], x["win_rate"]), reverse=True)

    # Format Breakdown
    all_raw_matches = get_matches(limit=1000, session_id=session_id)
    formats = {}
    for m in all_raw_matches:
        f = m["format"] or "Ranked Doubles"
        if f not in formats:
            formats[f] = {"format": f, "wins": 0, "losses": 0, "total": 0, "win_rate": 0.0}
        formats[f]["total"] += 1
        if m["result"] == "WIN":
            formats[f]["wins"] += 1
        elif m["result"] == "LOSS":
            formats[f]["losses"] += 1

    for f, d in formats.items():
        if d["total"] > 0:
            d["win_rate"] = round((d["wins"] / d["total"]) * 100, 1)

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": win_rate,
        "streak": f"{'W' if streak_type == 'WIN' else 'L' if streak_type == 'LOSS' else '-'}{streak_count}" if streak_count else "None",
        "opp_matchups": opp_matchups,
        "my_performance": my_performance,
        "formats": list(formats.values()),
        "active_session_id": get_active_session_id()
    }
