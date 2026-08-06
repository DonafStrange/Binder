from pathlib import Path
import sqlite3

from services.graph import GraphService


class CategoryService:

    def __init__(self):
        self.db_path = Path("database/database.db")
        self.graph = GraphService()
        self.create_table()

    def create_table(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            """
        )

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='works'"
        )
        has_works_table = cursor.fetchone() is not None

        if has_works_table:
            cursor.execute(
                """
                SELECT DISTINCT category
                FROM works
                WHERE category IS NOT NULL
                AND TRIM(category) != ''
                """
            )

            for (name,) in cursor.fetchall():
                self._ensure_category_exists(cursor, name)

        connection.commit()
        connection.close()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _normalize_name(self, name):
        return (name or "").strip()

    def _ensure_category_exists(self, cursor, name):
        normalized = self._normalize_name(name)
        if not normalized:
            return None

        cursor.execute(
            "SELECT id FROM categories WHERE LOWER(name) = LOWER(?)",
            (normalized,)
        )
        result = cursor.fetchone()

        if result is None:
            cursor.execute(
                "INSERT INTO categories(name) VALUES (?)",
                (normalized,)
            )
            return cursor.lastrowid

        return result[0]

    def get_all_categories(self):
        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, name FROM categories ORDER BY LOWER(name), name"
        )

        categories = [
            {"id": row[0], "name": row[1]}
            for row in cursor.fetchall()
        ]

        connection.close()

        return categories

    def add_category(self, name):
        normalized = self._normalize_name(name)
        if not normalized:
            return None

        if self.category_exists(normalized):
            return self.get_category_id(normalized)

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO categories(name) VALUES (?)",
            (normalized,)
        )
        category_id = cursor.lastrowid
        connection.commit()
        connection.close()

        self.graph.sync_works()

        return category_id

    def rename_category(self, category_id, new_name):
        normalized = self._normalize_name(new_name)
        if not normalized:
            return None

        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, name FROM categories WHERE id = ?",
            (category_id,)
        )
        result = cursor.fetchone()

        if result is None:
            connection.close()
            return None

        old_name = result[1]

        cursor.execute(
            "SELECT id FROM categories WHERE id != ? AND LOWER(name) = LOWER(?)",
            (category_id, normalized)
        )
        if cursor.fetchone() is not None:
            connection.close()
            return None

        cursor.execute(
            "UPDATE categories SET name = ? WHERE id = ?",
            (normalized, category_id)
        )

        cursor.execute(
            "UPDATE works SET category = ? WHERE LOWER(category) = LOWER(?)",
            (normalized, old_name)
        )

        connection.commit()
        connection.close()

        self.graph.sync_works()

        return category_id

    def delete_category(self, category_id, move_to=None, remove_from_works=False):
        connection = self._connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, name FROM categories WHERE id = ?",
            (category_id,)
        )
        result = cursor.fetchone()

        if result is None:
            connection.close()
            return {"deleted": False, "used": 0}

        category_name = result[1]

        cursor.execute(
            "SELECT COUNT(*) FROM works WHERE LOWER(category) = LOWER(?)",
            (category_name,)
        )
        usage_count = cursor.fetchone()[0]

        if usage_count > 0 and not move_to and not remove_from_works:
            connection.close()
            return {"deleted": False, "used": usage_count}

        if move_to:
            cursor.execute(
                "UPDATE works SET category = ? WHERE LOWER(category) = LOWER(?)",
                (move_to, category_name)
            )
        elif remove_from_works:
            cursor.execute(
                "UPDATE works SET category = '' WHERE LOWER(category) = LOWER(?)",
                (category_name,)
            )

        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))

        connection.commit()
        connection.close()

        self.graph.sync_works()

        return {"deleted": True, "used": usage_count}

    def category_exists(self, name):
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT 1 FROM categories WHERE LOWER(name) = LOWER(?)",
            (self._normalize_name(name),)
        )
        exists = cursor.fetchone() is not None
        connection.close()
        return exists

    def get_category_by_name(self, name):
        normalized = self._normalize_name(name)
        if not normalized:
            return None

        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, name FROM categories WHERE LOWER(name) = LOWER(?)",
            (normalized,)
        )
        row = cursor.fetchone()
        connection.close()

        if row is None:
            return None

        return {"id": row[0], "name": row[1]}

    def get_category_id(self, name):
        category = self.get_category_by_name(name)
        if category is None:
            return None
        return category["id"]

    def get_category_usage_count(self, name):
        normalized = self._normalize_name(name)
        if not normalized:
            return 0

        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM works WHERE LOWER(category) = LOWER(?)",
            (normalized,)
        )
        count = cursor.fetchone()[0]
        connection.close()
        return count
