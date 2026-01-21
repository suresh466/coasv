# multi-stage image build to create a final image without uv.

# First, build the application in the `/app` directory.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
# Ensures Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1
# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile` for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
# Install system dependencies:
# libpq-dev: Required for psycopg2 (PostgreSQL adapter)
# gcc: Required for compiling some Python packages
RUN apt-get update \
  && apt-get upgrade \
  && apt-get -y install python3-dev libpq-dev gcc --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-dev


# generate tailwindcss classes
FROM node:24-alpine AS tailwind
# copy entire app from builder
COPY --from=builder /app /app
WORKDIR /app/jstoolchain
# install and build Tailwind
RUN npm ci && npm run build


# Then, use a final image without uv
FROM python:3.13-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.
# libpq-dev is runtime dep for psycopg2
RUN apt-get update \
  && apt-get upgrade \
  && apt-get -y install libpq-dev --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*
# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
  && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app
# Copy built CSS from Node stage
COPY --from=tailwind --chown=nonroot:nonroot /app/common/static/css /app/common/static/css
# Place executables in the environment at the front of the path
# project deps are still installed in a venv and python links to system python executable
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app

# Create the staticfiles directory and set permissions
RUN mkdir -p /srv/staticfiles && chown nonroot:nonroot /srv/staticfiles

# Use the non-root user to run our application
USER nonroot
RUN chmod +x  /app/entrypoint.sh
# Set the entrypoint script as the default command
CMD ["/app/entrypoint.sh"]
