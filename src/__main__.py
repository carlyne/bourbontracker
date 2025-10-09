from __future__ import annotations

import os

import uvicorn

from src.settings import settings


def main() -> None:
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.environment == "local",
    )


if __name__ == "__main__":
    main()