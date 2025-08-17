#!/usr/bin/env sh
# Minimal production start script using gunicorn
# Note: ensure gunicorn is installed in the environment (pip install gunicorn)
# Runs the Flask `app` callable from main.py

# Workers and threads kept small to reduce resource usage on low-end machines
exec gunicorn -w 2 --threads 2 -b 0.0.0.0:8000 "main:app"
