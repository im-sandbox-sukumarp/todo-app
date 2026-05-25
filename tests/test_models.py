# -*- coding: utf-8 -*-

"""Unit tests for the TodoModel class."""

import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from todoapp.database import init_db, drop_db
from todoapp.models import TodoModel


class TodoModelTestCase(unittest.TestCase):
    """Test cases for the TodoModel CRUD operations."""

    def setUp(self):
        """Set up a temporary database for each test."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        init_db(self.db_path)
        self.model = TodoModel(self.db_path)

    def tearDown(self):
        """Remove the temporary database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_todo(self):
        """Test creating a todo returns correct data."""
        todo = self.model.create("Buy milk", "From the store", "high")
        self.assertIsNotNone(todo)
        self.assertEqual(todo["title"], "Buy milk")
        self.assertEqual(todo["description"], "From the store")
        self.assertEqual(todo["priority"], "high")
        self.assertEqual(todo["done"], False)
        self.assertIn("id", todo)
        self.assertIn("created_at", todo)
        self.assertIn("updated_at", todo)

    def test_create_todo_default_values(self):
        """Test creating a todo with default description and priority."""
        todo = self.model.create("Simple task")
        self.assertEqual(todo["title"], "Simple task")
        self.assertEqual(todo["description"], "")
        self.assertEqual(todo["priority"], "medium")

    def test_create_todo_invalid_priority(self):
        """Test creating a todo with an invalid priority raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.model.create("Task", priority="urgent")
        self.assertIn("Invalid priority", str(ctx.exception))
        self.assertIn("urgent", str(ctx.exception))

    def test_create_todo_all_priorities(self):
        """Test creating todos with each valid priority."""
        for priority in TodoModel.VALID_PRIORITIES:
            todo = self.model.create("Task %s" % priority, priority=priority)
            self.assertEqual(todo["priority"], priority)

    def test_get_by_id(self):
        """Test retrieving a todo by ID."""
        created = self.model.create("Test task")
        fetched = self.model.get_by_id(created["id"])
        self.assertEqual(fetched["title"], "Test task")
        self.assertEqual(fetched["id"], created["id"])

    def test_get_by_id_nonexistent(self):
        """Test retrieving a non-existent todo returns None."""
        result = self.model.get_by_id(9999)
        self.assertIsNone(result)

    def test_get_all(self):
        """Test retrieving all todos."""
        self.model.create("Task 1")
        self.model.create("Task 2")
        self.model.create("Task 3")
        todos = self.model.get_all()
        self.assertEqual(len(todos), 3)

    def test_get_all_empty(self):
        """Test retrieving todos when database is empty."""
        todos = self.model.get_all()
        self.assertEqual(len(todos), 0)

    def test_get_all_filter_done(self):
        """Test filtering out completed todos."""
        todo1 = self.model.create("Task 1")
        self.model.create("Task 2")
        self.model.update(todo1["id"], done=True)

        all_todos = self.model.get_all(show_done=True)
        self.assertEqual(len(all_todos), 2)

        pending_todos = self.model.get_all(show_done=False)
        self.assertEqual(len(pending_todos), 1)
        self.assertEqual(pending_todos[0]["title"], "Task 2")

    def test_update_title(self):
        """Test updating a todo's title."""
        todo = self.model.create("Original")
        updated = self.model.update(todo["id"], title="Updated")
        self.assertEqual(updated["title"], "Updated")

    def test_update_description(self):
        """Test updating a todo's description."""
        todo = self.model.create("Task", "Old description")
        updated = self.model.update(todo["id"], description="New description")
        self.assertEqual(updated["description"], "New description")

    def test_update_priority(self):
        """Test updating a todo's priority."""
        todo = self.model.create("Task", priority="low")
        updated = self.model.update(todo["id"], priority="high")
        self.assertEqual(updated["priority"], "high")

    def test_update_done(self):
        """Test marking a todo as done."""
        todo = self.model.create("Task")
        updated = self.model.update(todo["id"], done=True)
        self.assertEqual(updated["done"], True)

    def test_update_done_to_false(self):
        """Test marking a done todo as not done."""
        todo = self.model.create("Task")
        self.model.update(todo["id"], done=True)
        updated = self.model.update(todo["id"], done=False)
        self.assertEqual(updated["done"], False)

    def test_update_invalid_priority(self):
        """Test updating with an invalid priority raises ValueError."""
        todo = self.model.create("Task")
        with self.assertRaises(ValueError):
            self.model.update(todo["id"], priority="critical")

    def test_update_nonexistent(self):
        """Test updating a non-existent todo returns None."""
        result = self.model.update(9999, title="Nothing")
        self.assertIsNone(result)

    def test_update_no_changes(self):
        """Test update with no valid fields returns unchanged todo."""
        todo = self.model.create("Task")
        result = self.model.update(todo["id"], invalid_field="value")
        self.assertEqual(result["title"], "Task")

    def test_update_multiple_fields(self):
        """Test updating multiple fields at once."""
        todo = self.model.create("Task", "Desc", "low")
        updated = self.model.update(
            todo["id"], title="New Title", description="New Desc", priority="high"
        )
        self.assertEqual(updated["title"], "New Title")
        self.assertEqual(updated["description"], "New Desc")
        self.assertEqual(updated["priority"], "high")

    def test_delete(self):
        """Test deleting a todo."""
        todo = self.model.create("To delete")
        result = self.model.delete(todo["id"])
        self.assertTrue(result)
        self.assertIsNone(self.model.get_by_id(todo["id"]))

    def test_delete_nonexistent(self):
        """Test deleting a non-existent todo returns False."""
        result = self.model.delete(9999)
        self.assertFalse(result)

    def test_search_by_title(self):
        """Test searching todos by title."""
        self.model.create("Buy groceries")
        self.model.create("Walk the dog")
        self.model.create("Buy flowers")

        results = self.model.search("Buy")
        self.assertEqual(len(results), 2)

    def test_search_by_description(self):
        """Test searching todos by description."""
        self.model.create("Task 1", description="important meeting")
        self.model.create("Task 2", description="casual lunch")

        results = self.model.search("meeting")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Task 1")

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive (SQLite LIKE default)."""
        self.model.create("Buy MILK")
        results = self.model.search("milk")
        self.assertEqual(len(results), 1)

    def test_search_no_results(self):
        """Test search with no matches returns empty list."""
        self.model.create("Task")
        results = self.model.search("nonexistent")
        self.assertEqual(len(results), 0)

    def test_count_empty(self):
        """Test count with no todos."""
        stats = self.model.count()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["completed"], 0)

    def test_count_with_todos(self):
        """Test count with a mix of completed and pending todos."""
        todo1 = self.model.create("Task 1")
        self.model.create("Task 2")
        self.model.create("Task 3")
        self.model.update(todo1["id"], done=True)

        stats = self.model.count()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["completed"], 1)

    def test_row_to_dict_none(self):
        """Test _row_to_dict with None input."""
        result = self.model._row_to_dict(None)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
