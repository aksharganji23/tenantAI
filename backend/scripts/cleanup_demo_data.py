"""Create a backup and remove only the repository's known demo tenants.

This script is intentionally opt-in. It never runs during application startup.
Run from backend/ with `python scripts/cleanup_demo_data.py --apply`.
"""

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from app.config import settings
from app.database import SessionLocal
from app.models.tenant import Tenant


KNOWN_DEMO_SLUGS = {"technova", "greenleaf"}
KNOWN_DEMO_EMAILS = {
    "admin@tenantai.com",
    "admin@technova.com",
    "user@technova.com",
    "admin@greenleaf.com",
    "user@greenleaf.com",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Perform deletion after showing the matching records")
    args = parser.parse_args()

    database_path = Path(settings.DATABASE_URL.removeprefix("sqlite:///"))
    if not args.apply:
        print("Dry run only. Pass --apply to remove the known demo records.")

    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter(Tenant.slug.in_(KNOWN_DEMO_SLUGS)).all()
        print("Matching demo tenants:", ", ".join(f"{tenant.id}:{tenant.slug}" for tenant in tenants) or "none")
        if not args.apply or not tenants:
            return
        if database_path.exists():
            backup = database_path.with_name(
                f"{database_path.stem}.backup-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{database_path.suffix}"
            )
            shutil.copy2(database_path, backup)
            print(f"Database backup written to {backup}")
        for tenant in tenants:
            db.delete(tenant)
        db.commit()
        print("Removed only the known demo tenants and their cascading records.")
        print(f"Known demo emails reviewed: {', '.join(sorted(KNOWN_DEMO_EMAILS))}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
