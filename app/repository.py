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
        raise NotImplementedError("TODO: insert company into SQLite")

    # Method to reassign users from deprecated companies to target company
    async def reassign_users(self, source_company_ids: list[str], target_company_id: str) -> None:
        raise NotImplementedError("TODO: bulk update users.company_id to target_company_id")

    # Method to reassign branches from deprecated companies to target company
    async def reassign_branches(self, source_company_ids: list[str], target_company_id: str) -> None:
        raise NotImplementedError("TODO: bulk update branches.company_id to target_company_id")

    # Method to mark source companies as deleted in the database
    async def soft_delete_companies(self, source_company_ids: list[str]) -> None:
        raise NotImplementedError("TODO: mark source companies as deleted")
