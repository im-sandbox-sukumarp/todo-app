# -*- coding: utf-8 -*-

"""Todo model with CRUD operations."""

from todoapp.database import get_connection


class TodoModel(object):
    """Handles all database operations for todos."""

    VALID_PRIORITIES = ["low", "medium", "high"]

    def __init__(self, db_path=None):
        self.db_path = db_path

    def _get_conn(self):
        return get_connection(self.db_path)

    def _row_to_dict(self, row):
        """Convert a sqlite3.Row to a dictionary."""
        if row is None:
            return None
        d = {}
        for key in row.keys():
            d[key] = row[key]
        # Convert done field from int to bool
        if "done" in d:
            d["done"] = bool(d["done"])
        return d

    def get_all(self, show_done=True):
        """Return all todos, optionally filtering out completed ones."""
        conn = self._get_conn()
        cursor = conn.cursor()
        if show_done:
            cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM todos WHERE done = 0 ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return map(self._row_to_dict, rows)

    def get_by_id(self, todo_id):
        """Return a single todo by ID."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_dict(row)

    def create(self, title, description="", priority="medium"):
        """Create a new todo and return it."""
        if priority not in self.VALID_PRIORITIES:
            raise ValueError("Invalid priority: %s. Must be one of: %s" % (
                priority, ", ".join(self.VALID_PRIORITIES)))

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO todos (title, description, priority) VALUES (?, ?, ?)",
            (title, description, priority),
        )
        conn.commit()
        todo_id = cursor.lastrowid
        conn.close()
        return self.get_by_id(todo_id)

    def update(self, todo_id, **kwargs):
        """Update a todo by ID. Accepts title, description, priority, done."""
        todo = self.get_by_id(todo_id)
        if todo is None:
            return None

        allowed_fields = {"title", "description", "priority", "done"}
        updates = {}
        for key, value in kwargs.iteritems():
            if key in allowed_fields:
                updates[key] = value

        if not updates:
            return todo

        if "priority" in updates and updates["priority"] not in self.VALID_PRIORITIES:
            raise ValueError("Invalid priority: %s" % updates["priority"])

        if "done" in updates:
            updates["done"] = 1 if updates["done"] else 0

        set_clause = ", ".join(["%s = ?" % k for k in updates.keys()])
        values = updates.values() + [todo_id]

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE todos SET %s, updated_at = CURRENT_TIMESTAMP WHERE id = ?" % set_clause,
            values,
        )
        conn.commit()
        conn.close()
        return self.get_by_id(todo_id)

    def delete(self, todo_id):
        """Delete a todo by ID. Returns True if deleted, False if not found."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    def search(self, query):
        """Search todos by title or description."""
        conn = self._get_conn()
        cursor = conn.cursor()
        like_query = "%" + query + "%"
        cursor.execute(
            "SELECT * FROM todos WHERE title LIKE ? OR description LIKE ? ORDER BY created_at DESC",
            (like_query, like_query),
        )
        rows = cursor.fetchall()
        conn.close()
        return map(self._row_to_dict, rows)

    def count(self):
        """Return counts of total and completed todos."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as completed FROM todos")
        row = cursor.fetchone()
        conn.close()
        return {"total": row["total"], "completed": row["completed"] or 0}
