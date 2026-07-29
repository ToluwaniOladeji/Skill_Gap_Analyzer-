# Skill Gap Analyzer

Django implementation of the SRS in `Oladeji_Toluwani_Jephthae_Assignment2_06_29_2026.docx`.

## What Is Included

- Django 4 web application using Django templates and Bootstrap 5.
- Custom email-based authentication with registration, login, logout, password reset, and profile update.
- Role selection and 1-to-5 self-assessment forms with required completion.
- Gap calculation engine and readiness percentage service.
- Personalized learning path generator using internally managed resources.
- Assessment history, past results, Chart.js progress tracking, and skill comparison.
- Server-side PDF report generation using WeasyPrint.
- Django admin for roles, skills, role-skill requirements, learning resources, assessments, and graduate progress.
- Unit tests for core gap/readiness logic, access control, learning paths, and permanent assessment records.

## Requirements

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

On Windows, WeasyPrint also requires its native GTK/Pango libraries. If PDF
downloads return a 503 message mentioning `gobject-2.0-0`, install the native
dependencies from the WeasyPrint installation guide, then restart Django.

The SRS specifies MySQL 8.0+. Configure these environment variables before running normally:

```powershell
$env:MYSQL_DATABASE="skill_gap_analyzer"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your-password"
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
```

For local smoke testing without MySQL, set:

```powershell
$env:DATABASE_ENGINE="sqlite"
```

## Run

```powershell
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Test

```powershell
$env:DJANGO_SETTINGS_MODULE="skillgap.settings_test"
python manage.py test
```

## Requirement Trace

- FR 1.1-FR 1.6: `analyzer/forms.py`, `analyzer/views.py`, `skillgap/urls.py`, login-required decorators.
- FR 2.1-FR 2.6: role selection, assessment form, submit flow, `Assessment` and `AssessmentSkillRating`.
- FR 3.1-FR 3.5: `analyzer/services.py::compute_gap`.
- FR 4.1-FR 4.4: `analyzer/services.py::generate_learning_path` and results template.
- FR 5.1-FR 5.4: history and progress views/templates.
- FR 6.1-FR 6.3: `analyzer/pdf.py` and report download view.
- FR 7.1-FR 7.5: `analyzer/admin.py`.
- NFR 1-NFR 6: Django auth, PBKDF2, CSRF, ownership filtering, staff admin, 60-minute sessions.
- NFR 7-NFR 10: simple indexed queries, eager loading, service tests, and fast in-process calculation.
- NFR 11-NFR 13: English-only labels, onboarding alert, form labels/helper text.
- NFR 14-NFR 15: permanent assessment records and PDF reports.
- NFR 16-NFR 17: Bootstrap responsive templates for current Chrome, Edge, Firefox, PC, Android, and iOS browsers.
- NFR 18-NFR 19: single Django app responsibility and Django TestCase coverage.
- NFR 20-NFR 23: enforced in views, services, models, and tests.
