# pytfredon-hw

Lightweight hardware monitor (Flask backend + lightweight frontend).

Quick start (development):

1. Create a virtualenv and install dependencies:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Run dev server:

```sh
uv run main.py
```

Production (example):

```sh
sh start.sh
```

Tests (requires server running at http://127.0.0.1:8000):

```sh
pytest -q
```

Notes:

- GPU libraries (`pynvml`, `pyamdgpuinfo`) are optional and detected at runtime.
- The frontend polls `/api/hwinfo` with exponential backoff to reduce load.
