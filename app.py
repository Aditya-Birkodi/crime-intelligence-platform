"""Convenience / AppSail entrypoint: python3 -u app.py

Listens on X_ZOHO_CATALYST_LISTEN_PORT (AppSail) or APP_PORT / 8000 (local).

AppSail requires the process to bind the listen port within ~10s — do not
pip-install at startup. Dependencies are vendored into .appsail_vendor via
app-config.json scripts.predeploy.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
VENDOR = ROOT / ".appsail_vendor"

# Vendored deps (AppSail deploy) take precedence over system site-packages
if VENDOR.is_dir() and str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

# Ensure backend package imports resolve before uvicorn loads the app
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
os.chdir(ROOT)


def main() -> None:
    import uvicorn

    port = int(
        os.getenv("X_ZOHO_CATALYST_LISTEN_PORT") or os.getenv("APP_PORT") or "8000"
    )
    host = os.getenv("APP_HOST", "0.0.0.0")
    reload = os.getenv("APP_RELOAD", "false").lower() in {
        "1",
        "true",
        "yes",
    } and not os.getenv("X_ZOHO_CATALYST_LISTEN_PORT")

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
