# SpotKick — World Cup 2026 Penalty Predictor

**Live at:** [spotkick.app](https://spotkick.app) *(update with your URL)*

A free, privacy-first AI that predicts penalty kick success rates for any football player. **Now covering all 48 World Cup 2026 nations.**

**No login. No tracking. No ads. 100% free forever.**

---

## 🌍 World Cup 2026 Coverage

- **48 nations** — every team in the tournament
- **99 players** — primary and secondary penalty takers
- **2,041 penalty events** — career history for every player
- **12 groups (A-L)** — filter by group
- Real data where available, realistic estimates for emerging nations

---

## 🚀 Quick Start (3 Minutes)

```bash
cd spotkick
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# Open index.html in your browser
```

---

## 📊 All 48 Nations & Their Penalty Takers

| Group | Nation | Primary Taker | Backup |
|-------|--------|---------------|--------|
| A | 🇲🇽 Mexico | Raul Jimenez | — |
| A | 🇿🇦 South Africa | Oswin Appollis | Lyle Foster |
| A | 🇰🇷 South Korea | Son Heung-Min | Hwang Hee-Chan |
| A | 🇨🇿 Czechia | Patrik Schick | Tomas Soucek |
| B | 🇨🇦 Canada | Jonathan David | — |
| B | 🇶🇦 Qatar | Akram Afif | Almoez Ali |
| B | 🇨🇭 Switzerland | Granit Xhaka | Breel Embolo |
| B | 🇧🇦 Bosnia | Edin Dzeko | Ermedin Demirovic |
| C | 🇧🇷 Brazil | Neymar | Raphinha |
| C | 🇲🇦 Morocco | Brahim Diaz | Ayoub El Kaabi |
| C | 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland | Scott McTominay | John McGinn |
| C | 🇭🇹 Haiti | Duckens Nazon | Wilson Isidor |
| D | 🇺🇸 USA | Christian Pulisic | Folarin Balogun |
| D | 🇵🇾 Paraguay | Julio Enciso | Miguel Almiron |
| D | 🇦🇺 Australia | Ajdin Hrustic | Nestory Irankunda |
| D | 🇹🇷 Turkey | Hakan Calhanoglu | Arda Guler |
| E | 🇩🇪 Germany | Kai Havertz | Joshua Kimmich |
| E | 🇨🇮 Ivory Coast | Franck Kessie | Ibrahim Sangare |
| E | 🇪🇨 Ecuador | Enner Valencia | Jordy Caicedo |
| E | 🇨🇼 Curacao | Leandro Bacuna | Jordi Paulina |
| F | 🇳🇱 Netherlands | Memphis Depay | Cody Gakpo |
| F | 🇯🇵 Japan | Ayase Ueda | Ritsu Doan |
| F | 🇸🇪 Sweden | Viktor Gyokeres | Alexander Isak |
| F | 🇹🇳 Tunisia | Ali Abdi | Elias Achouri |
| G | 🇧🇪 Belgium | Kevin De Bruyne | Romelu Lukaku |
| G | 🇪🇬 Egypt | Mohamed Salah | Omar Marmoush |
| G | 🇮🇷 Iran | Mehdi Taremi | Sardar Azmoun |
| G | 🇳🇿 New Zealand | Chris Wood | Ben Waine |
| H | 🇪🇸 Spain | Mikel Oyarzabal | Lamine Yamal |
| H | 🇨🇻 Cape Verde | Ryan Mendes | Garry Rodrigues |
| H | 🇸🇦 Saudi Arabia | Salem Al-Dawsari | Firas Al Buraikan |
| H | 🇺🇾 Uruguay | Federico Valverde | Darwin Nunez |
| I | 🇫🇷 France | Kylian Mbappe | Ousmane Dembele |
| I | 🇸🇳 Senegal | Sadio Mane | Nicolas Jackson |
| I | 🇳🇴 Norway | Erling Haaland | Martin Odegaard |
| I | 🇮🇶 Iraq | Aymen Hussein | Amir Al-Ammari |
| J | 🇦🇷 Argentina | Lionel Messi | Julian Alvarez |
| J | 🇩🇿 Algeria | Riyad Mahrez | Mohamed Amoura |
| J | 🇦🇹 Austria | Marko Arnautovic | Marcel Sabitzer |
| J | 🇯🇴 Jordan | Ali Olwan | Mousa Tamari |
| K | 🇵🇹 Portugal | Cristiano Ronaldo | Bruno Fernandes |
| K | 🇺🇿 Uzbekistan | Eldor Shomurodov | Otabek Shukurov |
| K | 🇨🇴 Colombia | James Rodriguez | Luis Diaz |
| K | 🇨🇩 DR Congo | Yoane Wissa | Cedric Bakambu |
| L | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | Harry Kane | Marcus Rashford |
| L | 🇭🇷 Croatia | Luka Modric | Andrej Kramaric |
| L | 🇬🇭 Ghana | Jordan Ayew | Mohammed Kudus |
| L | 🇵🇦 Panama | Ismael Diaz | Cecilio Waterman |

---

## ☁️ Deploy to the Internet

See **[DOMAIN_GUIDE.md](DOMAIN_GUIDE.md)** for complete step-by-step instructions.

**Quick version:**
1. Buy domain on Namecheap (~$12/year)
2. Deploy backend to Railway (free)
3. Deploy frontend to Vercel (free)
4. Point domain DNS to Vercel
5. Update `API_URL` in `index.html`

**Total cost: $12/year**

---

## 🗃️ Database Versions

The backend auto-detects the best available database:

1. `penalties_worldcup2026.db` — 99 players, 48 nations, 2,041 events ⭐ **CURRENT**
2. `penalties_real.db` — 49 players, 1,565 events (fallback)
3. `penalties.db` — 15 players, 841 events (seed fallback)

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI backend (auto-detects best DB) |
| `index.html` | Cinematic frontend |
| `penalties_worldcup2026.db` | **World Cup 2026 database** |
| `DOMAIN_GUIDE.md` | Step-by-step domain setup |
| `LAUNCH_TWEETS.md` | 26 tweets + TikTok scripts |
| `Dockerfile` | Container build |
| `railway.json` | Railway deployment |
| `vercel.json` | Vercel deployment |
| `deploy.sh` | Server deployment script |

---

## 🎵 Audio Player

Built-in player ready for licensed music. **Do NOT use copyrighted tracks without permission.**

See `index.html` for instructions on adding your own audio file.

---

## 📝 License

MIT — build something amazing.

**Built for the World Cup. Free forever. No strings attached.** 🏆⚽
