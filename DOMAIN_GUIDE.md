# SpotKick Domain Pointing Guide
# ================================
# How to connect your custom domain to SpotKick
# Estimated time: 15 minutes
# Cost: ~$12/year for domain + $0 for hosting

---

## STEP 1: Buy a Domain (5 minutes)

### Recommended registrars:
1. **Namecheap** (namecheap.com) — $8-15/year, free WHOIS privacy
2. **Porkbun** (porkbun.com) — $8-12/year, clean UI
3. **Cloudflare Registrar** — At-cost pricing (~$9/year), no markup
4. **Google Domains** — Now Squarespace, but still reliable

### Domain name ideas:
- spotkick.app (premium, ~$15-20/year)
- spotkick.io (~$35/year)
- spotkick.co (~$12/year)
- spotkick.xyz (~$2-5/year)
- spotkick.fyi (~$12/year)
- penaltypredictor.com (~$12/year)
- worldcuppens.com (~$12/year)
- spotkick.org (~$12/year)

**My recommendation:** spotkick.app or spotkick.co

### How to buy:
1. Go to namecheap.com
2. Search "spotkick"
3. Add .app or .co to cart
4. Create account, checkout
5. Enable WHOIS privacy (free on Namecheap)

---

## STEP 2: Deploy Backend to Railway (5 minutes)

Railway gives you free hosting for small projects.

### 2A. Create Railway Account
1. Go to railway.app
2. Sign up with GitHub (fastest)
3. Verify email

### 2B. Connect Your Repo
1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select your SpotKick repository
5. Railway auto-detects the Dockerfile

### 2C. Get Your API URL
1. After deployment, Railway gives you a URL like:
   `https://spotkick-api.up.railway.app`
2. Copy this URL — you'll need it for the frontend
3. Test it: `https://spotkick-api.up.railway.app/`
   Should return: `{"status": "live", ...}`

### 2D. (Optional) Custom Domain for Backend
If you want the API on a subdomain:
1. In Railway, go to your service Settings
2. Click "Custom Domain"
3. Add `api.spotkick.app`
4. Railway gives you a CNAME record
5. Add that CNAME to your DNS (see Step 4)

---

## STEP 3: Deploy Frontend to Vercel (3 minutes)

Vercel hosts static sites for free.

### 3A. Create Vercel Account
1. Go to vercel.com
2. Sign up with GitHub

### 3B. Deploy
**Option A: Drag and Drop (Fastest)**
1. Go to vercel.com/new
2. Drag your `index.html` file into the upload area
3. Vercel deploys instantly
4. Get URL: `https://spotkick-abc123.vercel.app`

**Option B: GitHub Repo (Better for updates)**
1. In Vercel, click "Add New Project"
2. Import your GitHub repo
3. Framework preset: "Other"
4. Deploy

### 3C. Update API URL
In your `index.html`, find this line:
```javascript
const API_URL = "http://localhost:8000";
```

Change it to your Railway URL:
```javascript
const API_URL = "https://spotkick-api.up.railway.app";
```

Redeploy to Vercel if using GitHub, or re-upload if using drag-and-drop.

---

## STEP 4: Point Domain to Vercel (5 minutes)

This is where the magic happens. You tell your domain to show the Vercel site.

### 4A. Get Vercel DNS Records
1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your domain: `spotkick.app`
4. Vercel shows you what DNS records to add

Typically Vercel asks for:
- **A Record**: `@` → `76.76.21.21` (Vercel's IP)
- **CNAME Record**: `www` → `cname.vercel-dns.com`

### 4B. Add DNS Records at Your Registrar

**Namecheap instructions:**
1. Log into Namecheap
2. Go to Domain List → Manage → Advanced DNS
3. Delete any existing A records or CNAME records
4. Add new records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | 76.76.21.21 | Automatic |
| CNAME Record | www | cname.vercel-dns.com | Automatic |

**If using Cloudflare DNS (recommended for speed):**
1. Sign up at cloudflare.com
2. Add your domain
3. Cloudflare scans your DNS records
4. Replace Namecheap nameservers with Cloudflare's:
   - `lara.ns.cloudflare.com`
   - `greg.ns.cloudflare.com`
5. In Cloudflare DNS tab, add the same A and CNAME records
6. Enable "Always Use HTTPS" and "Auto Minify"

### 4C. Verify
1. Wait 5-30 minutes for DNS to propagate
2. Go to `https://spotkick.app`
3. Should show your SpotKick website
4. Test the predictor: type "Messi" → should return prediction

---

## STEP 5: SSL/HTTPS (Free, Auto-Enabled)

Both Vercel and Railway provide free SSL certificates automatically.

- Vercel: Auto-issues Let's Encrypt certificate
- Railway: Auto-issues certificate for custom domains

Your site will be `https://` secure within minutes of domain connection.

---

## STEP 6: Test Everything (2 minutes)

### Backend test:
```bash
curl https://spotkick-api.up.railway.app/
# Should return: {"status": "live", "players": 99, "nations": 48}

curl "https://spotkick-api.up.railway.app/predict/Lionel%20Messi"
# Should return Messi's prediction
```

### Frontend test:
1. Open `https://spotkick.app`
2. Type "Ronaldo" in the chatbox
3. Should show prediction card with 83.6% career rate

### Full flow test:
1. Open `https://spotkick.app` on your phone
2. Type "Kylian Mbappe"
3. Select "Knockout" context
4. Should show: ~84% predicted probability

---

## TROUBLESHOOTING

### "Site not found" on domain
- DNS hasn't propagated yet. Wait 30 minutes.
- Check DNS records are correct in Namecheap/Cloudflare
- Use whatsmydns.net to check propagation globally

### "Cannot connect to API" in frontend
- Check `API_URL` in `index.html` matches your Railway URL
- Check Railway service is running (not sleeping)
- Check CORS is enabled in `main.py` (it is by default)

### "Player not found" error
- Backend is using wrong database. Check Railway logs.
- Make sure `penalties_worldcup2026.db` is in the repo
- The backend auto-detects: World Cup > Real > Seed

### Domain shows "404" on Vercel
- Domain not properly connected in Vercel settings
- Go to Vercel → Project → Settings → Domains → Verify

---

## COST BREAKDOWN

| Item | Cost | Notes |
|------|------|-------|
| Domain (spotkick.co) | $12/year | Namecheap |
| Railway hosting | $0/month | Free tier sufficient |
| Vercel hosting | $0/month | Free tier unlimited |
| Cloudflare DNS | $0/month | Free plan |
| SSL certificate | $0 | Auto from Vercel/Railway |
| **Total** | **$12/year** | |

---

## ALTERNATIVE: Single-Server Deployment

If you want everything on ONE server (simpler but less scalable):

### Use a VPS ($5/month on DigitalOcean/Linode/AWS Lightsail)

```bash
# 1. SSH into your server
ssh root@your-server-ip

# 2. Install Docker
curl -fsSL https://get.docker.com | sh

# 3. Clone your repo
git clone https://github.com/yourname/spotkick.git
cd spotkick

# 4. Build and run
docker-compose up -d

# 5. Install Nginx
apt install nginx -y

# 6. Configure Nginx
cat > /etc/nginx/sites-available/spotkick << 'EOF'
server {
    listen 80;
    server_name spotkick.app www.spotkick.app;

    location / {
        root /var/www/spotkick;
        index index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
    }
}
EOF

ln -s /etc/nginx/sites-available/spotkick /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# 7. Copy frontend
mkdir -p /var/www/spotkick
cp index.html /var/www/spotkick/

# 8. Restart Nginx
systemctl restart nginx

# 9. SSL with Certbot
apt install certbot python3-certbot-nginx -y
certbot --nginx -d spotkick.app -d www.spotkick.app

# Done! https://spotkick.app is live
```

---

## QUICK REFERENCE: DNS RECORDS

For spotkick.app pointing to Vercel + Railway:

```
; A Record — points root domain to Vercel
@       IN A     76.76.21.21

; CNAME — points www to Vercel
www     IN CNAME cname.vercel-dns.com.

; CNAME — points API to Railway (optional)
api     IN CNAME spotkick-api.up.railway.app.
```

---

## NEXT STEPS AFTER DOMAIN IS LIVE

1. **Test on mobile** — iPhone Safari, Android Chrome
2. **Share the URL** — Twitter, Reddit, Discord
3. **Add to Google Search Console** — search.google.com/search-console
4. **Add Google Analytics** (optional) — only if you want traffic data
5. **Create social media accounts** — @SpotKickEngine on Twitter
6. **Post launch thread** — use LAUNCH_TWEETS.md

---

## SUPPORT

If you get stuck:
- Vercel docs: vercel.com/docs/concepts/projects/custom-domains
- Railway docs: docs.railway.app/deploy/exposing-your-app
- Namecheap DNS: namecheap.com/support/knowledgebase/article/319/2237/
- Cloudflare DNS: developers.cloudflare.com/dns/manage-dns-records/

---

**Your domain will be live within 30 minutes of following this guide.**

Good luck. 🏆⚽
