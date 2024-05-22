#!/bin/bash
# entrypoint.sh

# Wait for the PostgreSQL database to be ready
while ! nc -z $COASV_DB_HOST 5432; do
  echo "Waiting for PostgreSQL database..."
  sleep 1
done

# Run Django migrations
python manage.py migrate

# Start the Django development server
python manage.py runserver 0.0.0.0:8000
