# syntax=docker/dockerfile:1
FROM python:3.13
# Python environment variables:
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app/

EXPOSE 8000

# ensure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

# Install Python dependencies without storing pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint script as the default command
# This will run migrations, collect static files, and start Gunicorn
CMD ["/app/entrypoint.sh"]
