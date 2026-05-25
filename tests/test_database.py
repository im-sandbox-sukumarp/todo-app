# -*- coding: utf-8 -*-

"""Unit tests for the database module."""

import os
import sys
import unittest
import tempfile
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from todoapp.database import init_db, drop_db, get_connection


class DatabaseTestCase(unittest.TestCase):
    """Test cases for database initialization and utilities."""

    def setUp(self):
        """Set up a temporary database file."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")

    def tearDown(self):
        """Remove the temporary database file."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_init_db_creates_todos_table(self):
        """Test that init_db creates the todos table."""
        init_db(self.db_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='todos'"
        )
        result = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "todos")

    def test_init_db_idempotent(self):
        """Test that init_db can be called multiple times without error."""
        init_db(self.db_path)
        init_db(self.db_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='todos'"
        )
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)

    def test_init_db_schema(self):
        """Test that the todos table has the expected columns."""
        init_db(self.db_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(todos)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        expected = {"id", "title", "description", "priority", "done", "created_at", "updated_at"}
        self.assertEqual(columns, expected)

    def test_drop_db(self):
        """Test that drop_db removes the todos table."""
        init_db(self.db_path)
        drop_db(self.db_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='todos'"
        )
        result = cursor.fetchone()
        conn.close()
        self.assertIsNone(result)

    def test_get_connection_returns_row_factory(self):
        """Test that get_connection sets row_factory to sqlite3.Row."""
        conn = get_connection(self.db_path)
        self.assertEqual(conn.row_factory, sqlite3.Row)
        conn.close()

    def test_get_connection_functional(self):
        """Test that the connection returned can execute queries."""
        init_db(self.db_path)
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (title) VALUES (?)", ("Test",))
        conn.commit()
        cursor.execute("SELECT title FROM todos")
        row = cursor.fetchone()
        self.assertEqual(row["title"], "Test")
        conn.close()


if __name__ == "__main__":
    unittest.main()
