"""
SpotKick Data Scraper Template
================================
This is a starter template for scraping penalty data from football statistics sites.
Run this to expand your database beyond the seed players.

Targets:
- Transfermarkt (player penalty stats)
- FBref (detailed match events)
- Understat (shot data)

WARNING: Respect robots.txt and rate limits. Use responsibly.
"""

import sqlite3
import httpx
from bs4 import BeautifulSoup
import time
import re

DB_PATH = "penalties.db"

class PenaltyScraper:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=30.0
        )

    def add_player(self, name, country, position):
        """Add a new player to the database"""
        self.cursor.execute("""
            INSERT OR IGNORE INTO players (name, country, position)
            VALUES (?, ?, ?)
        """, (name, country, position))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_penalty_event(self, player_id, match_data):
        """Add a single penalty event"""
        self.cursor.execute("""
            INSERT INTO penalty_events 
            (player_id, match_id, competition, opponent, match_context, minute, 
             result, direction, height, goalkeeper, pressure_score, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id,
            match_data.get("match_id"),
            match_data.get("competition"),
            match_data.get("opponent"),
            match_data.get("context", "unknown"),
            match_data.get("minute", 0),
            match_data.get("result"),
            match_data.get("direction", "unknown"),
            match_data.get("height", "unknown"),
            match_data.get("goalkeeper", "unknown"),
            match_data.get("pressure", 0.5),
            match_data.get("date")
        ))
        self.conn.commit()

    def scrape_transfermarkt_penalties(self, player_url):
        """
        Example: Scrape penalty stats from a Transfermarkt player profile
        player_url: e.g., "https://www.transfermarkt.com/lionel-messi/elfmetertore/spieler/28003"
        """
        try:
            response = self.client.get(player_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Parse penalty table — customize selectors based on actual page structure
            table = soup.find('table', {'class': 'items'})
            if not table:
                return []

            penalties = []
            for row in table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 5:
                    penalties.append({
                        "competition": cells[0].text.strip(),
                        "date": cells[1].text.strip(),
                        "result": "scored" if "tor" in cells[2].text.lower() else "missed",
                        "opponent": cells[3].text.strip(),
                        "context": "league"  # Infer from competition
                    })

            return penalties

        except Exception as e:
            print(f"Scrape error: {e}")
            return []

    def scrape_fbref_shootouts(self, player_name):
        """
        FBref has detailed shootout data.
        Search for player, then parse penalty shootout tables.
        """
        search_url = f"https://fbref.com/en/search/search.fcgi?search={player_name.replace(' ', '+')}"
        # Implementation depends on FBref's current structure
        pass

    def update_player_stats(self, player_id):
        """Recalculate aggregate stats from events"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN result = 'scored' THEN 1 ELSE 0 END) as scored,
                SUM(CASE WHEN match_context = 'shootout' THEN 1 ELSE 0 END) as so_total,
                SUM(CASE WHEN match_context = 'shootout' AND result = 'scored' THEN 1 ELSE 0 END) as so_scored
            FROM penalty_events 
            WHERE player_id = ?
        """, (player_id,))

        total, scored, so_total, so_scored = self.cursor.fetchone()

        conversion = round(scored / total * 100, 1) if total > 0 else 0
        so_conversion = round(so_scored / so_total * 100, 1) if so_total > 0 else 0

        # Find favorite direction
        self.cursor.execute("""
            SELECT direction, COUNT(*) as count
            FROM penalty_events
            WHERE player_id = ? AND result = 'scored'
            GROUP BY direction
            ORDER BY count DESC
            LIMIT 1
        """, (player_id,))

        fav_dir = self.cursor.fetchone()
        favorite = fav_dir[0] if fav_dir else "unknown"

        self.cursor.execute("""
            UPDATE players SET
                total_penalties_taken = ?,
                total_scored = ?,
                conversion_rate = ?,
                shootout_taken = ?,
                shootout_scored = ?,
                shootout_rate = ?,
                favorite_direction = ?
            WHERE id = ?
        """, (total, scored, conversion, so_total, so_scored, so_conversion, favorite, player_id))

        self.conn.commit()

    def close(self):
        self.client.close()
        self.conn.close()


if __name__ == "__main__":
    scraper = PenaltyScraper()

    # Example usage:
    # pid = scraper.add_player("New Player", "Country", "Forward")
    # penalties = scraper.scrape_transfermarkt_penalties("https://...")
    # for p in penalties:
    #     scraper.add_penalty_event(pid, p)
    # scraper.update_player_stats(pid)

    scraper.close()
    print("Scraper ready. Customize the URLs and selectors for your targets.")
