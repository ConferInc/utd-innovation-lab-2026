import os
import sys
from pathlib import Path


def pytest_configure() -> None:
    week7_dir = Path(__file__).resolve().parents[1]
    if str(week7_dir) not in sys.path:
        sys.path.insert(0, str(week7_dir))
    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/week7_test")
