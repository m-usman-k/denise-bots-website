# Denise Bots Website

A premium Django-based dashboard for managing the Denise Bots ecosystem.

## Features
- **Discord OAuth2 Integration**: Secure login for administrators.
- **Super Admin Control**: Main admin (`simpleprog`) can manage other bot administrators.
- **Centralized Database**: All bots share a single SQLite3 database with the website for real-time synchronization.
- **Unified Dashboard**: Monitor bot status, donations, and user stats in one place.
- **Modern UI**: High-performance, glassmorphism-inspired dark theme.

## Tech Stack
- **Backend**: Django 4.2+, SQLite3
- **Authentication**: Django-allauth (Discord)
- **Frontend**: Vanilla CSS & JavaScript (Modern Aesthetics)
- **Deployment**: Whitenoise for static files, Gunicorn/Psycopg2 ready.

## Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure `.env`**:
   - Create a `.env` file based on `.env.example`.
   - Add your `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`.
3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```
4. **Start the server**:
   ```bash
   python manage.py runserver
   ```

## Bot Migration
The bots have been updated to use a centralized database system. Each bot now imports `SharedDatabase` from the root directory, ensuring all operations (donations, tickets, etc.) are reflected in real-time on the website dashboard.

## Dashboard Access
Access the dashboard at `/dashboard/`. Initial access is restricted to the main admin (`simpleprog`). Other admins can be added via the "Manage Admins" section in the dashboard.
