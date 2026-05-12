import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import settings


def main() -> None:
    output_dir = Path(os.getenv("BACKUP_OUTPUT_DIR", "backups"))
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_path = output_dir / f"qalam-backup-{timestamp}.dump"

    command = [
        "pg_dump",
        "--format=custom",
        "--no-owner",
        "--no-acl",
        f"--file={backup_path}",
        settings.database_url,
    ]
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    print(f"Backup created: {backup_path}")


if __name__ == "__main__":
    main()
