
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import json
import os
from typing import Optional, List
from dataclasses import dataclass, asdict

app = FastAPI(title="SpotKick API", version="4.0", docs_url="/docs")

# WIDE OPEN CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Auto-detect best database: World Cup 2026 > Real > Seed
if os.path.exists("penalties_worldcup2026.db"):
    DB_PATH = "penalties_worldcup2026.db"
    DB_VERSION = "worldcup2026"
elif os.path.exists("penalties_real.db"):
    DB_PATH = "penalties_real.db"
    DB_VERSION = "real"
else:
    DB_PATH = "penalties.db"
    DB_VERSION = "seed"

def get_db():
    return sqlite3.connect(DB_PATH)

@dataclass
class PenaltyPrediction:
    player_name: str
    country: str
    overall_conversion_rate: float
    predicted_score_probability: float
    confidence: str
    total_penalties: int
    shootout_conversion_rate: float
    favorite_direction: str
    direction_breakdown: dict
    context_analysis: dict
    recent_form: list
    ai_insight: str
    key_factors: list
    wc_group: str
    is_primary_taker: int

@app.get("/")
def root():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM players")
    player_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT country) FROM players")
    nation_count = cursor.fetchone()[0]
    conn.close()

    return {
        "message": "SpotKick API — World Cup 2026 Penalty Intelligence",
        "status": "live",
        "db_version": DB_VERSION,
        "players": player_count,
        "nations": nation_count,
        "privacy": "No auth. No tracking. No logs.",
        "endpoints": {
            "players": "/players",
            "search": "/search?q=NAME",
            "predict": "/predict/{player_name}?context=knockout",
            "nations": "/nations"
        }
    }

@app.get("/nations")
def list_nations():
    """Return all nations and their primary takers"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT country, wc_group, COUNT(*) as players,
               SUM(CASE WHEN is_primary_taker = 1 THEN 1 ELSE 0 END) as primary_takers
        FROM players GROUP BY country, wc_group ORDER BY wc_group, country
    """)
    rows = cursor.fetchall()
    conn.close()
    return {
        "nations": len(rows),
        "groups": list(set([r[1] for r in rows])),
        "countries": [
            {"country": r[0], "group": r[1], "players": r[2], "primary_takers": r[3]}
            for r in rows
        ]
    }

@app.get("/players")
def list_players(group: Optional[str] = None):
    """Return all players. Filter by group if provided."""
    conn = get_db()
    cursor = conn.cursor()

    if group:
        cursor.execute("""
            SELECT name, country, position, total_penalties_taken, conversion_rate, 
                   favorite_direction, wc_group, is_primary_taker
            FROM players WHERE wc_group = ? ORDER BY total_penalties_taken DESC
        """, (group.upper(),))
    else:
        cursor.execute("""
            SELECT name, country, position, total_penalties_taken, conversion_rate, 
                   favorite_direction, wc_group, is_primary_taker
            FROM players ORDER BY total_penalties_taken DESC
        """)

    rows = cursor.fetchall()
    conn.close()
    return {
        "count": len(rows),
        "filter": group.upper() if group else "all",
        "players": [
            {
                "name": r[0], "country": r[1], "position": r[2],
                "total_penalties": r[3], "conversion_rate": r[4],
                "favorite_direction": r[5], "group": r[6], "primary": bool(r[7])
            }
            for r in rows
        ]
    }

@app.get("/search")
def search_players(q: str = Query(..., min_length=1)):
    """Fuzzy search for player names"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, country, conversion_rate, total_penalties_taken, 
               favorite_direction, wc_group, is_primary_taker
        FROM players 
        WHERE name LIKE ? 
        ORDER BY is_primary_taker DESC, total_penalties_taken DESC 
        LIMIT 10
    """, (f"%{q}%",))
    results = cursor.fetchall()
    conn.close()
    return {
        "query": q,
        "results": [
            {
                "name": r[0], "country": r[1], "conversion_rate": r[2],
                "total": r[3], "favorite": r[4], "group": r[5], "primary": bool(r[6])
            }
            for r in results
        ]
    }

@app.get("/predict/{player_name}")
def predict_penalty(player_name: str, context: Optional[str] = "knockout"):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, country, position, total_penalties_taken, total_scored, 
               conversion_rate, shootout_taken, shootout_scored, shootout_rate, 
               favorite_direction, wc_group, is_primary_taker
        FROM players WHERE LOWER(name) = LOWER(?)

    """, (player_name,))

    player = cursor.fetchone()
    if not player:
        return JSONResponse(status_code=404, content={"error": "Player not found"})

    (pid, name, country, position, total_taken, total_scored, base_rate, 
     so_taken, so_scored, so_rate, fav_dir, wc_group, is_primary) = player

    # Directional breakdown
    cursor.execute("""
        SELECT direction, result, COUNT(*) as count
        FROM penalty_events WHERE player_id = ? GROUP BY direction, result
    """, (pid,))
    dir_rows = cursor.fetchall()

    direction_stats = {"left": {"scored": 0, "missed": 0, "total": 0, "rate": 0.0},
                       "right": {"scored": 0, "missed": 0, "total": 0, "rate": 0.0},
                       "center": {"scored": 0, "missed": 0, "total": 0, "rate": 0.0}}

    for direction, result, count in dir_rows:
        if direction in direction_stats:
            direction_stats[direction]["total"] += count
            if result == "scored":
                direction_stats[direction]["scored"] += count
            else:
                direction_stats[direction]["missed"] += count

    for d in direction_stats:
        total = direction_stats[d]["total"]
        if total > 0:
            direction_stats[d]["rate"] = round(direction_stats[d]["scored"] / total * 100, 1)

    # Context-specific stats
    cursor.execute("""
        SELECT result, COUNT(*) as count
        FROM penalty_events WHERE player_id = ? AND match_context = ? GROUP BY result
    """, (pid, context))

    context_rows = cursor.fetchall()
    context_scored = sum(r[1] for r in context_rows if r[0] == "scored")
    context_total = sum(r[1] for r in context_rows)
    context_rate = round(context_scored / context_total * 100, 1) if context_total > 0 else base_rate

    # Recent form (last 10)
    cursor.execute("""
        SELECT result, direction, match_context, competition, date
        FROM penalty_events WHERE player_id = ? ORDER BY date DESC LIMIT 10
    """, (pid,))
    recent = cursor.fetchall()
    recent_form = [{"result": r[0], "direction": r[1], "context": r[2], "competition": r[3], "date": r[4]} for r in recent]

    conn.close()

    # PREDICTION ENGINE
    predicted_prob = base_rate

    if context == "shootout":
        predicted_prob = so_rate if so_taken > 0 else base_rate * 0.92
    elif context == "knockout":
        predicted_prob = base_rate * 0.95
    elif context == "group_stage":
        predicted_prob = base_rate * 1.02

    if len(recent_form) >= 5:
        recent_5_scored = sum(1 for r in recent_form[:5] if r["result"] == "scored")
        recent_5_rate = recent_5_scored / 5 * 100
        predicted_prob = predicted_prob * 0.7 + recent_5_rate * 0.3

    if total_taken > 100:
        predicted_prob = predicted_prob * 0.95 + 78.0 * 0.05

    predicted_prob = round(max(0, min(100, predicted_prob)), 1)

    if total_taken >= 50:
        confidence = "High" if predicted_prob > 85 or predicted_prob < 65 else "Medium"
    elif total_taken >= 20:
        confidence = "Medium"
    else:
        confidence = "Low — limited sample size"

    insights = []
    if context == "shootout" and so_taken > 0:
        if so_rate > base_rate:
            insights.append(f"Clutch performer: {so_rate}% in shootouts vs {base_rate}% overall")
        else:
            insights.append(f"Shootout vulnerability: drops to {so_rate}% under ultimate pressure")

    if direction_stats[fav_dir]["rate"] > 90:
        insights.append(f"Deadly to the {fav_dir}: {direction_stats[fav_dir]['rate']}% when going that way")

    if recent_form and recent_form[0]["result"] == "missed":
        insights.append("Coming off a miss — mentally interesting to watch")
    elif recent_form and len(recent_form) >= 2 and recent_form[0]["result"] == "scored" and recent_form[1]["result"] == "scored":
        insights.append("On a scoring streak — confidence high")

    if total_taken > 100:
        insights.append(f"Veteran taker: {total_taken} penalties shows elite nerve")

    if base_rate > 90:
        insights.append(f"Elite conversion rate: {base_rate}% — among the best in history")
    elif base_rate < 75:
        insights.append(f"Below-average conversion: {base_rate}% — keeper has a chance")

    if not is_primary:
        insights.append("Backup taker — may not step up unless primary is unavailable")

    ai_insight = " | ".join(insights) if insights else f"Solid, reliable taker at {base_rate}% overall."

    key_factors = [
        f"Base conversion rate: {base_rate}%",
        f"Context-adjusted rate: {context_rate}%",
        f"Favorite direction: {fav_dir} ({direction_stats[fav_dir]['rate']}% success)",
        f"Total sample size: {total_taken} penalties"
    ]

    prediction = PenaltyPrediction(
        player_name=name, country=country, overall_conversion_rate=base_rate,
        predicted_score_probability=predicted_prob, confidence=confidence,
        total_penalties=total_taken, shootout_conversion_rate=so_rate,
        favorite_direction=fav_dir, direction_breakdown=direction_stats,
        context_analysis={"context": context, "context_rate": context_rate, "context_total": context_total},
        recent_form=recent_form[:5], ai_insight=ai_insight, key_factors=key_factors,
        wc_group=wc_group, is_primary_taker=is_primary
    )

    return asdict(prediction)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
