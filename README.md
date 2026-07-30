# Skill Gap Analyzer

A Django web platform that helps graduates identify exactly which skills they're missing for a target tech role, calculates a readiness score, and recommends a personalized, prioritized learning path to close the gap.

Live deployment: **https://toluwanistu.tech**

---

## Tech Stack

- **Backend:** Django 4.2, Python 3.8+
- **Database:** MySQL (SQLite supported for quick local testing)
- **Email:** SMTP (Brevo recommended — free tier, 300 emails/day)
- **PDF generation:** WeasyPrint
- **Frontend:** Django templates, Bootstrap 5, custom CSS
- **Static files:** Whitenoise (production)

---

## Prerequisites

Install these before starting:

- **Python 3.8 or higher** — check with `python3 --version`
- **pip** — check with `pip3 --version`
- **Git** — check with `git --version`
- **MySQL Server 8.0+** (or use SQLite for a quicker local setup — see the note in Step 4)

If any of these are missing:

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git mysql-server -y
```

**On Windows:** install [Python](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads), and [MySQL](https://dev.mysql.com/downloads/installer/) from their official installers.

**On macOS:**
```bash
brew install python git mysql
```

---

## Step-by-Step Setup

### 1. Clone the repository

```bash
git clone https://github.com/ToluwaniOladeji/Skill_Gap_Analyzer-.git
cd Skill_Gap_Analyzer-
```

### 2. Create and activate a virtual environment

**On macOS/Linux/Git Bash:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You'll know it's active when your terminal prompt is prefixed with `(.venv)`.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you're on Linux and this fails while installing `mysqlclient`, install its system build dependencies first, then retry:
```bash
sudo apt install python3-dev default-libmysqlclient-dev build-essential pkg-config -y
pip install -r requirements.txt
```

**PDF generation (WeasyPrint) also needs system-level libraries** that aren't installed via pip. Without these, PDF report downloads will fail with a clear error message, but the rest of the app works fine:
```bash
sudo apt install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2 libffi-dev shared-mime-info fonts-liberation
```
(macOS: `brew install pango cairo gdk-pixbuf`. Windows: PDF generation is easiest via WSL or a Linux server — WeasyPrint's native Windows support is limited.)

### 4. Set up the database

**Option A — MySQL (recommended, matches production):**

Log into MySQL and create a database and user:
```bash
sudo mysql -u root -p
```
```sql
CREATE DATABASE skill_gap_analyzer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'skillgap_app'@'localhost' IDENTIFIED BY 'choose-a-password';
GRANT ALL PRIVILEGES ON skill_gap_analyzer.* TO 'skillgap_app'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Option B — SQLite (fastest way to just try the project locally, no MySQL install needed):**

You'll set `DATABASE_ENGINE=sqlite` in the `.env` file in the next step, and Django will create a local `db.sqlite3` file automatically — no database server required at all.

### 5. Create your `.env` file

Create a file named `.env` in the project root (same folder as `manage.py`):

```bash
touch .env
```

Paste in the following, adjusting values as needed:

```
# --- Core Django settings ---
DJANGO_SECRET_KEY=replace-this-with-a-real-random-string
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# --- Database ---
# Use "sqlite" for the quick local option, or "mysql" if you set up Option A above
DATABASE_ENGINE=sqlite
MYSQL_DATABASE=skill_gap_analyzer
MYSQL_USER=skillgap_app
MYSQL_PASSWORD=choose-a-password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306

# --- Email (Brevo SMTP — leave DJANGO_DEBUG=1 and these blank to just print emails to your terminal instead) ---
DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@skillgap.local
```

**Generate a real secret key** rather than leaving the placeholder:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```
Copy the output into `DJANGO_SECRET_KEY` above.

**About email:** for local development, leaving `DJANGO_EMAIL_BACKEND` set to the console backend (as shown above) means password reset emails print directly to your terminal instead of actually sending — perfectly fine for testing the flow without needing real SMTP credentials. To send real emails, sign up free at [brevo.com](https://www.brevo.com), get your SMTP login and key from Settings → SMTP & API, and fill in `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`, then change `DJANGO_EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend`.

### 6. Run database migrations

```bash
python manage.py migrate
```

This creates all the necessary tables (users, job roles, skills, assessments, etc.) — no data yet, just the empty structure.

### 7. Seed demo data

The app is empty without this step — no job roles, skills, or learning resources exist until you run:

```bash
python manage.py seed_demo_data
```

You should see `Demo data seeded.` at the end. This populates 3 job roles (Web Developer, Data Analyst, IT Support Specialist), 15 skills per role, and curated learning resources for each skill at 3 difficulty levels. Safe to re-run any time — it updates existing records rather than duplicating them.

### 8. Create an admin account

```bash
python manage.py createsuperuser
```

Follow the prompts (email, full name, password) — this account can log into `/admin/` to manage roles, skills, and view aggregated graduate progress.

### 9. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser. You should land on the login page.

- Register a new graduate account to try the full assessment flow, or
- Log in at **http://127.0.0.1:8000/admin/** with your superuser account to manage content

---

## Running the Automated Tests

```bash
python manage.py test
```

This runs the existing test suite covering gap calculation accuracy, readiness percentage math, learning path filtering, cross-user data access restriction, and login enforcement.

---

## Project Structure

```
Skill_Gap_Analyzer-/
├── manage.py
├── requirements.txt
├── .env                          # you create this — never commit it
├── skillgap/                     # project-level config
│   ├── settings.py
│   ├── settings_test.py
│   ├── urls.py
│   └── wsgi.py
├── analyzer/                     # the main Django app
│   ├── models.py                 # User, JobRole, Skill, Assessment, LearningResource, etc.
│   ├── views.py
│   ├── forms.py
│   ├── admin.py                  # Django admin config + custom graduate-progress page
│   ├── services.py               # gap calculation + learning path logic
│   ├── pdf.py                    # PDF report generation
│   ├── tests.py
│   └── management/commands/
│       └── seed_demo_data.py     # populates roles/skills/resources
├── templates/
│   ├── base.html
│   ├── registration/             # login, register, password reset flow
│   ├── analyzer/                 # dashboard, assessment, results, etc.
│   └── admin/analyzer/           # custom admin templates
└── static/analyzer/styles.css
```

---

## Common Setup Issues

| Problem | Fix |
|---|---|
| `mysqlclient` fails to install | Install system build deps first (see Step 3), or just use SQLite for local dev |
| Site loads but shows no job roles | You skipped Step 7 — run `python manage.py seed_demo_data` |
| Password reset "sends" but nothing arrives | You're using the console backend (expected in local dev) — check your terminal, the email is printed there. For real delivery, set up Brevo SMTP credentials |
| PDF download fails with a message about GTK/Pango | WeasyPrint's system libraries aren't installed — see the note under Step 3 |
| `DisallowedHost` error | Add whatever hostname you're using to `DJANGO_ALLOWED_HOSTS` in `.env` |
| `500` error with nothing in the terminal | Set `DJANGO_DEBUG=1` in `.env` while developing locally — Django will show you the full traceback in the browser |

---

## Deploying to Production

Production deployment (2 load-balanced servers, Nginx + Gunicorn, HAProxy, HTTPS via Let's Encrypt, MySQL) is a separate, more involved process than local setup. See the deployment runbook for full details if you're setting up a production environment rather than just running this locally.

Key production differences from local setup:
- `DJANGO_DEBUG=0` (never leave debug mode on in production)
- Real `DJANGO_ALLOWED_HOSTS` matching your actual domain
- `DJANGO_SECURE_SSL=1` once HTTPS is configured
- Gunicorn + Nginx instead of `manage.py runserver`
- `python manage.py collectstatic --noinput` to gather static files for Whitenoise/Nginx to serve
