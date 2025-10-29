#!/usr/bin/env sh

# Wait for PostgreSQL using Python (no extra dependencies needed)
python <<'EOF'
import socket
import time
import os

host = os.environ.get('COASV_DB_HOST', 'localhost')
port = int(os.environ.get('COASV_DB_PORT', 5432))

print(f"Waiting for PostgreSQL at {host}:{port}...")

while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((host, port))
        sock.close()
        print("PostgreSQL is up and ready!")
        break
    except (socket.error, socket.timeout):
        print("PostgreSQL is unavailable - sleeping")
        time.sleep(1)
EOF

# Now run your Django commands
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 coas_view.wsgi:application
