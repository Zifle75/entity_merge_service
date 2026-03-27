import os
import sqlite3
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "demo_entity_merge.db"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def seed_database(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM branches")
        conn.execute("DELETE FROM companies")

        company_rows = [
            (
                "company-1",
                "Acme Corp",
                "123 Main St",
                None,
                "CA",
                "Los Angeles",
                "90001",
                10000,
                0,
            ),
            (
                "company-2",
                "Acme Corp",
                "123 Main St",
                None,
                "CA",
                "Los Angeles",
                "90001",
                10000,
                0,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO companies (
                id,
                name,
                address_line_1,
                address_line_2,
                state,
                city,
                postal_code,
                credit_limit,
                is_deleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            company_rows,
        )

        user_rows = [
            ("user-1", "Ari", "West", "company-1"),
            ("user-2", "Sam", "East", "company-2"),
        ]
        conn.executemany(
            "INSERT INTO users (id, first_name, last_name, company_id) VALUES (?, ?, ?, ?)",
            user_rows,
        )

        branch_rows = [
            ("branch-1", "HQ", "company-1"),
            ("branch-2", "HQ", "company-2"),
        ]
        conn.executemany(
            "INSERT INTO branches (id, name, company_id) VALUES (?, ?, ?)",
            branch_rows,
        )


def verify_merge(db_path: Path, merged_company_id: str) -> None:
    with sqlite3.connect(db_path) as conn:
        users_reassigned = conn.execute(
            "SELECT COUNT(*) FROM users WHERE company_id = ?", (merged_company_id,)
        ).fetchone()[0]
        branches_reassigned = conn.execute(
            "SELECT COUNT(*) FROM branches WHERE company_id = ?", (merged_company_id,)
        ).fetchone()[0]
        source_deleted = conn.execute(
            """
            SELECT COUNT(*)
            FROM companies
            WHERE id IN ('company-1', 'company-2') AND is_deleted = 1
            """
        ).fetchone()[0]

    print(f"Users reassigned: {users_reassigned}")
    print(f"Branches reassigned: {branches_reassigned}")
    print(f"Source companies soft-deleted: {source_deleted}")

    if users_reassigned != 2 or branches_reassigned != 2 or source_deleted != 2:
        raise SystemExit("Merge verification failed")


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    # Must be set before importing app.main so repository uses this db file.
    os.environ["DATABASE_PATH"] = str(DB_PATH)

    from app.main import app  # noqa: PLC0415

    # Importing app initializes schema through repository constructor.
    seed_database(DB_PATH)

    payload = {
        "source_company_1_id": "company-1",
        "source_company_2_id": "company-2",
        "resolved_company": {
            "name": "Acme Corp",
            "address": {
                "line_1": "123 Main St",
                "line_2": None,
                "state": "CA",
                "city": "Los Angeles",
                "postal_code": "90001",
            },
            "credit_limit": 10000,
        },
    }

    client = TestClient(app)
    response = client.post("/v1/company-merges", json=payload)

    print(f"HTTP {response.status_code}")
    print(response.json())

    if response.status_code != 200:
        raise SystemExit("Merge request failed")

    merged_company_id = response.json()["merged_company_id"]
    verify_merge(DB_PATH, merged_company_id)

    print("Demo merge completed successfully")


if __name__ == "__main__":
    main()
