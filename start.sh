#!/bin/sh
# 1. Run the auto-restore command (Migrates, creates user, imports data)
echo "🏗️ Starting Auto-Restore Process..."
python manage.py restore_sandbox

# 2. Start the web server
echo "🚀 Starting Gunicorn server..."
gunicorn marketplace_mock.wsgi:application --bind 0.0.0.0:8000
