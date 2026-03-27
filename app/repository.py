import sqlite3

from app.models import Company

# DAO class, can write different implenetations if we want to swap out SQLite for another database in the future.
class SqliteRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    address_line_1 TEXT NOT NULL,
                    address_line_2 TEXT,
                    state TEXT NOT NULL,
                    city TEXT NOT NULL,
                    postal_code TEXT NOT NULL,
                    credit_limit INTEGER,
                    is_deleted INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    company_id TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS branches (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    company_id TEXT NOT NULL
                );
                """
            )

    # Method to insert a company into the database.
    async def insert_company(self, company: Company) -> None:
        with self._connect() as conn:
            conn.execute(
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
                (
                    company.id,
                    company.name,
                    company.address.line_1,
                    company.address.line_2,
                    company.address.state,
                    company.address.city,
                    company.address.postal_code,
                    company.credit_limit,
                    1 if company.is_deleted else 0,
                ),
            )

    async def active_company_exists(self, company_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM companies WHERE id = ? AND is_deleted = 0 LIMIT 1",
                (company_id,),
            ).fetchone()
            return row is not None

    # Method to reassign users from deprecated companies to target company
    async def reassign_users(self, source_company_ids: list[str], target_company_id: str) -> None:
        if not source_company_ids:
            return

        placeholders = ",".join(["?"] * len(source_company_ids))
        query = f"UPDATE users SET company_id = ? WHERE company_id IN ({placeholders})"

        with self._connect() as conn:
            conn.execute(query, [target_company_id, *source_company_ids])

    # Method to reassign branches from deprecated companies to target company
    async def reassign_branches(self, source_company_ids: list[str], target_company_id: str) -> None:
        if not source_company_ids:
            return

        placeholders = ",".join(["?"] * len(source_company_ids))
        query = f"UPDATE branches SET company_id = ? WHERE company_id IN ({placeholders})"

        with self._connect() as conn:
            conn.execute(query, [target_company_id, *source_company_ids])

    # Method to mark source companies as deleted in the database
    async def soft_delete_companies(self, source_company_ids: list[str]) -> None:
        if not source_company_ids:
            return

        placeholders = ",".join(["?"] * len(source_company_ids))
        query = f"UPDATE companies SET is_deleted = 1 WHERE id IN ({placeholders})"

        with self._connect() as conn:
            conn.execute(query, source_company_ids)
