"""Convenience entrypoint: python app.py

FastAPI still runs on Uvicorn under the hood — this just wraps the CLI.
Equivalent to:
  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --app-dir .
"""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"


def main() -> None:
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    reload = os.getenv("APP_RELOAD", "true").lower() in {"1", "true", "yes"}

    # Ensure `import app` / `from main import app` resolve when reloading
    os.chdir(ROOT)
    if str(BACKEND) not in os.sys.path:
        os.sys.path.insert(0, str(BACKEND))

    uvicorn.run(
        "main:app",
        app_dir=str(BACKEND),
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(BACKEND)] if reload else None,
    )


if __name__ == "__main__":
    main()
