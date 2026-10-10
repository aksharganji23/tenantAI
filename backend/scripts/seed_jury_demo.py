"""Seed the local database with the safe, repeatable jury demonstration data.

Run from backend/ with:
    python scripts/seed_jury_demo.py
"""

from app.seed.seed_data import JURY_PASSWORD, run_seed


def main() -> None:
    run_seed()
    print()
    print("Jury demo accounts")
    print("==================")
    print("TechNova Solutions")
    print("  Admin: admin@technova.com / " + JURY_PASSWORD)
    print("  User:  user@technova.com / " + JURY_PASSWORD)
    print()
    print("GreenLeaf Retail")
    print("  Admin: admin@greenleaf.com / " + JURY_PASSWORD)
    print("  User:  user@greenleaf.com / " + JURY_PASSWORD)
    print()
    print("Superadmin (global dashboard)")
    print("  Email: admin@tenantai.com / SuperAdmin123!")
    print()
    print("These are local demonstration credentials. Do not use them in production.")


if __name__ == "__main__":
    main()
