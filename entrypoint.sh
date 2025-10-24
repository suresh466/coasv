#!/usr/bin/env sh

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 coas_view.wsgi:application
