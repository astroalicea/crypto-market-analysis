# Deploying to AWS EC2

Step-by-step guide to put the dashboard on a public URL. Each step ends with a **✅ Check**. Don't move on until it passes.

## What you're building

```
Browser ──HTTP:80──► nginx ──► gunicorn (127.0.0.1:8000) ──► Django ──► SQLite
                       │
                       └──► /static/ files served straight from disk

cron (every 15 min) ──► python manage.py fetch_coins ──► SQLite
```

- **gunicorn** is the *application server*. It runs your Python code and keeps several worker processes alive. `runserver` is single-threaded, isn't security-hardened, and Django's docs say never to use it in production.
- **nginx** is the *web server / reverse proxy*. It faces the internet, handles slow clients and many connections cheaply, serves static files without touching Python, and passes everything else to gunicorn. Later it's where HTTPS gets configured.
- **systemd** keeps gunicorn running: it starts gunicorn on boot and restarts it if it crashes.
- **cron** runs the pipeline on a schedule so the dashboard updates itself.

---

## Step 0: Push the code

The server pulls from GitHub, so make sure `main` is pushed (including `deploy/` and the `gunicorn` line in `requirements.txt`).

✅ **Check:** `git status` says "up to date with 'origin/main'", and you can see the `deploy/` folder on GitHub.

## Step 1: Launch the instance (AWS Console)

EC2 → **Launch instance**:

| Setting | Value | Why |
|---|---|---|
| Name | `crypto-dashboard` | |
| AMI | **Ubuntu Server 24.04 LTS** | Ships Python 3.12, which Django 6 requires |
| Instance type | `t3.micro` or `t2.micro`, whichever is marked *Free tier eligible* | 1 GB RAM is enough for 2 workers |
| Key pair | **Create new** → `crypto-dashboard`, type ED25519, format `.pem` | Downloads once. Lose it and you lose SSH access. |
| Network → Security group | Create new, with these rules: | |
| | SSH, port 22, source **My IP** | Only your IP can try to log in |
| | HTTP, port 80, source **Anywhere (0.0.0.0/0)** | The public website |
| Storage | 8 GB gp3 (default) | |

Click **Launch**. Then **Elastic IPs → Allocate → Associate** it with the instance. Without an Elastic IP, your public IP changes every time the instance stops, and `ALLOWED_HOSTS` breaks.

> 💰 AWS bills public IPv4 addresses hourly (a few dollars a month) and instance hours outside the free tier. **Set a billing alarm** (Billing → Budgets → create a $5 budget) before going further.

✅ **Check:** the instance shows **Running** with both status checks passed, and you've written down the Elastic IP (called `YOUR_IP` below).

## Step 2: SSH in (on your Mac)

```bash
mv ~/Downloads/crypto-dashboard.pem ~/.ssh/
chmod 400 ~/.ssh/crypto-dashboard.pem      # ssh refuses keys that other users can read
ssh -i ~/.ssh/crypto-dashboard.pem ubuntu@YOUR_IP
```

Type `yes` to the fingerprint prompt the first time.

✅ **Check:** your prompt changes to `ubuntu@ip-...:~$`. **Every step below runs on the server** unless it says otherwise.

## Step 3: Install system packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nginx git
```

✅ **Check:** `python3 --version` shows 3.12.x. Visiting `http://YOUR_IP` in your browser shows "Welcome to nginx!", which proves the security group and nginx both work.

## Step 4: Get the code

The app goes in `/srv`, not your home folder. Ubuntu 24.04 makes home directories private, so nginx couldn't read the static files from there.

```bash
sudo mkdir -p /srv/crypto-market-analysis
sudo chown ubuntu:ubuntu /srv/crypto-market-analysis
git clone https://github.com/astroalicea/crypto-market-analysis.git /srv/crypto-market-analysis
cd /srv/crypto-market-analysis

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

✅ **Check:** `pip show gunicorn` prints version 23.0.0.

## Step 5: Production `.env`

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
nano .env
```

Paste in the following, using the generated key and your IP:

```
DJANGO_SECRET_KEY=<the key you just generated>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=YOUR_IP
```

Save with `Ctrl+O`, `Enter`, then `Ctrl+X`. Then lock the file down:

```bash
chmod 600 .env
```

Use a **new** secret key, not the one on your laptop. Each environment gets its own secrets, so a leak in one doesn't compromise the other.

✅ **Check:** `python manage.py check --deploy` runs. It will print warnings about HTTPS/HSTS, which is expected until you have a domain. It must **not** print errors.

## Step 6: Database, static files, first data load

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py fetch_coins
```

✅ **Check:** the last line says `Run 1: saved 20 coin snapshots.`, and `ls staticfiles` shows an `admin` folder.

## Step 7: Smoke test gunicorn by hand

Before handing gunicorn to systemd, prove it can serve the app:

```bash
gunicorn --bind 127.0.0.1:8000 crypto_dashboard.wsgi:application &
curl -s -o /dev/null -w "%{http_code}\n" -H "Host: YOUR_IP" http://127.0.0.1:8000/
kill %1
```

✅ **Check:** the curl prints `200`. A `400` means `DJANGO_ALLOWED_HOSTS` doesn't match the Host header.

## Step 8: Run gunicorn as a service

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
```

`enable` means "start on boot." `--now` means "and start it right now."

✅ **Check:** `sudo systemctl status gunicorn` shows **active (running)** in green. Press `q` to exit.

## Step 9: Point nginx at gunicorn

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/crypto-market-analysis
sudo ln -s /etc/nginx/sites-available/crypto-market-analysis /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default      # otherwise the welcome page keeps winning
sudo nginx -t
sudo systemctl reload nginx
```

✅ **Check:** `http://YOUR_IP` shows **your dashboard** with the coin table and chart. `http://YOUR_IP/static/admin/css/base.css` shows CSS text, not a 404 or 403. 🎉 **You have a live URL.**

## Step 10: Keep the data fresh with cron

```bash
crontab -e      # pick nano if asked
```

Add this line at the bottom:

```
*/15 * * * * cd /srv/crypto-market-analysis && venv/bin/python manage.py fetch_coins >> /home/ubuntu/fetch_coins.log 2>&1
```

This runs every 15 minutes. `>> ... 2>&1` appends both normal output and errors to a log file. Cron jobs have no terminal, so without it, failures would vanish silently.

✅ **Check:** after 15 minutes, `tail /home/ubuntu/fetch_coins.log` shows a new `Run N: saved 20 coin snapshots.` line, and the "last updated" time on the dashboard has moved.

---

## Deploying updates later

```bash
ssh -i ~/.ssh/crypto-dashboard.pem ubuntu@YOUR_IP
cd /srv/crypto-market-analysis && source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

## When something breaks

| Symptom | Where to look |
|---|---|
| **502 Bad Gateway** | nginx is up but gunicorn isn't. Run `sudo systemctl status gunicorn` and `sudo journalctl -u gunicorn -n 50`. |
| **400 Bad Request** | The address you typed isn't in `DJANGO_ALLOWED_HOSTS`. Fix `.env`, then `sudo systemctl restart gunicorn`. |
| **Page loads, but the admin has no styling** | Static files are missing. Re-run `collectstatic` and check the `alias` path in the nginx config. |
| **"Welcome to nginx!"** | The default site is still enabled (Step 9). |
| **Browser times out** | Check that the security group allows port 80, and that you're using `http://`, not `https://`. |
| **Dashboard data is stale** | `tail /home/ubuntu/fetch_coins.log`. CoinGecko errors (rate limits, timeouts) show up here. |
| nginx errors | `sudo tail /var/log/nginx/error.log` |

## Known limitations (next steps)

- **HTTP only.** Traffic is unencrypted. Don't create an admin superuser on this server until HTTPS is set up, because the password would cross the internet in plain text. Next step: a domain name + Let's Encrypt (`certbot --nginx`).
- **SQLite.** Fine for one server with one writer (cron). It becomes a problem once there are multiple servers or concurrent writes. Then move to PostgreSQL (RDS).
- **Manual deploys.** The "deploying updates" commands above are a candidate for a GitHub Actions workflow.

## Shutting it down

To stop paying: EC2 → **Terminate** the instance, then **Elastic IPs → Release**. An Elastic IP that isn't attached to anything still costs money.
