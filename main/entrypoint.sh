#!/bin/sh

# Run Django management commands
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn on the correct port
exec gunicorn -w 3 -b 0.0.0.0:${GUNICORN_PORT} config.wsgi:application