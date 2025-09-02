Project Guidelines: Service_Portal

Overview
- This is a standard Django project created with django-admin startproject. Two local apps are present: portal and users. We aim to adhere to Django defaults wherever possible to keep setup simple and predictable.

Python/Django
- Django: 5.2.x (settings header indicates 5.2.5)
- Python: Use a recent Python compatible with Django 5.2 (3.10+ recommended).

Shell/CLI Policy
- Do not use Windows PowerShell for project commands.
- Use Windows Command Prompt (cmd) or invoke tasks via Python (e.g., python manage.py ...) instead.
- Prefer manage.py for all Django-related actions (runserver, migrate, makemigrations, test, shell).

Quick Start (Development)
1) Create and activate a virtual environment (optional but recommended)
   - py -3 -m venv .venv
   - .venv\Scripts\activate
2) Install dependencies
   - pip install -r requirements.txt
   - If requirements.txt is missing, install Django 5.2 and any extras you need, then freeze:
     pip install "Django>=5.2,<6" && pip freeze > requirements.txt
3) Run migrations (uses default sqlite3 database db.sqlite3)
   - python manage.py migrate
4) Create a superuser (for admin access)
   - python manage.py createsuperuser
5) Run the development server (default runserver)
   - python manage.py runserver
6) Access the site
   - http://127.0.0.1:8000/portal
   - Admin: http://127.0.0.1:8000/admin/

Configuration (Stick to Django Defaults)
- manage.py is the entry point for all tasks (runserver, migrate, makemigrations, test).
- settings module: Service_Portal.settings
- Database: Default sqlite3 at BASE_DIR/db.sqlite3 (no additional configuration needed for dev).
- Installed apps include: django.contrib.* defaults, users, portal.
- Templates: APP_DIRS=True with per-app templates. No custom TEMPLATES["DIRS"] paths used.
- Static files: STATIC_URL = "/static/". No custom STATICFILES_DIRS defined; use app-level static directories by default (e.g., portal/static/...).
- Authentication: Custom user model is configured via AUTH_USER_MODEL = "users.User". Create users via createsuperuser or admin.
- Login URL: LOGIN_URL = "portal:login".
- Internationalization: Defaults to LANGUAGE_CODE = "en-us", TIME_ZONE = "UTC", USE_TZ = True.

Environment Variables
- For development, defaults in settings.py are sufficient. For production, set environment variables (through your chosen process manager or deployment tool):
  - SECRET_KEY: Do NOT use the development key in production.
  - DEBUG: Set to False in production.
  - ALLOWED_HOSTS: Add your domain(s) or server IPs.
  - DATABASE_URL or equivalent: If moving away from sqlite, configure DATABASES accordingly (stick to Django’s DATABASES structure).

# Dont use frameworks and libraries except these 
- Django
- Django-environ
- Django-extensions
- Django-filter
- Django-rest-framework
- Django-rest-framework-simplejwt
- Django-simple-history
- Django-storages
- Django-widget-tweaks
- Bootstrap

Migrations Workflow
- When changing models:
  - python manage.py makemigrations
  - python manage.py migrate
- Keep migrations in each app’s migrations/ directory (default behavior).

Testing
- Use Django’s default test runner:
  - python manage.py test
- Place tests in tests.py or a tests/ package within each app (portal/tests.py, users/tests.py already exist).

Apps and Code Organization
- users app: Contains the custom User model (AUTH_USER_MODEL = users.User). Add user-related admin, views, urls here.
- portal app: Domain logic for the portal (models, forms, views, templates under portal/templates/portal/).
- URLs: Project-level urls in Service_Portal/urls.py include app URLs. App-level urls are in portal/urls.py and users/urls.py.
- Templates: Use app templates with the structure portal/templates/portal/*.html to leverage APP_DIRS=True.

Admin
- Admin is enabled by default (django.contrib.admin in INSTALLED_APPS). After creating a superuser, log into /admin.

Static and Media
- Static: By default, place static files under each app’s static/<app_name>/ directory. Example: portal/static/portal/...
- Media: Not explicitly configured. If needed later, add MEDIA_URL and MEDIA_ROOT in settings.py following Django defaults and update URL patterns for development serving.

Localization
- Locale middleware is enabled; LANGUAGES list is currently guarded by an if False block. If you need multiple languages later, remove the guard and run makemessages/compilemessages per Django docs. Stick to Django’s i18n framework.

Deployment Notes (Simple/Django-Default leaning)
- Use collectstatic only if STATIC_ROOT is configured (for production). In this project, STATIC_ROOT isn’t set; add it when deploying.
- WSGI entry: Service_Portal.wsgi.application (default). ASGI is also present if needed.
- Keep settings simple; avoid custom loaders or non-standard settings unless necessary.

Common Commands
- Start app: python manage.py startapp <appname>
- Shell: python manage.py shell
- Check: python manage.py check
- Show URLs: python manage.py show_urls (if django-extensions installed; otherwise omit)

Conventions and Principles
- Favor Django defaults to reduce configuration:
  - Use manage.py for all actions.
  - Use app templates/static locations with APP_DIRS=True.
  - Use the default SQLite database in development.
  - Use Django’s authentication and admin as provided, with the configured custom user model.
- Keep settings minimal; avoid environment-specific branches in code. Use environment variables and .env (via django-environ) only if needed, otherwise keep defaults.

Troubleshooting
- If migrations fail due to model changes, try:
  - Delete un-applied migration file you just created (not historical ones), fix the model, run makemigrations again.
- If templates aren’t loading, ensure they are in portal/templates/portal/ and that app is in INSTALLED_APPS.
- If static files don’t appear in development, ensure you reference them with {% load static %} and proper paths and that files are under app static directories.
