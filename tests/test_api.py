# -*- coding: utf-8 -*-

"""Tests for the Todo List Manager API."""

import json
import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from todoapp.app import create_app
from todoapp.database import init_db, drop_db


class TodoApiTestCase(unittest.TestCase):
    """Test cases for the Todo API endpoints."""

    def setUp(self):
        """Set up test client and initialize test database."""
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            init_db(self.app.config["DATABASE"])

    def tearDown(self):
        """Clean up test database."""
        with self.app.app_context():
            drop_db(self.app.config["DATABASE"])

    def _create_todo(self, title="Test Todo", description="Test Description", priority="medium"):
        """Helper to create a todo via the API."""
        return self.client.post(
            "/api/todos",
            data=json.dumps({
                "title": title,
                "description": description,
                "priority": priority,
            }),
            content_type="application/json",
        )

    def test_index(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("name", data)

    def test_create_todo(self):
        """Test creating a new todo."""
        response = self._create_todo()
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["todo"]["title"], "Test Todo")
        self.assertEqual(data["todo"]["priority"], "medium")
        self.assertEqual(data["todo"]["done"], False)

    def test_create_todo_without_title(self):
        """Test creating a todo without a title fails."""
        response = self.client.post(
            "/api/todos",
            data=json.dumps({"description": "No title"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_todo_invalid_priority(self):
        """Test creating a todo with invalid priority fails."""
        response = self._create_todo(priority="urgent")
        self.assertEqual(response.status_code, 400)

    def test_list_todos(self):
        """Test listing all todos."""
        self._create_todo(title="First")
        self._create_todo(title="Second")
        response = self.client.get("/api/todos")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["todos"]), 2)

    def test_get_todo(self):
        """Test getting a single todo."""
        create_resp = self._create_todo()
        todo_id = json.loads(create_resp.data)["todo"]["id"]
        response = self.client.get("/api/todos/%d" % todo_id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["todo"]["title"], "Test Todo")

    def test_get_nonexistent_todo(self):
        """Test getting a todo that doesn't exist."""
        response = self.client.get("/api/todos/9999")
        self.assertEqual(response.status_code, 404)

    def test_update_todo(self):
        """Test updating a todo."""
        create_resp = self._create_todo()
        todo_id = json.loads(create_resp.data)["todo"]["id"]
        response = self.client.put(
            "/api/todos/%d" % todo_id,
            data=json.dumps({"title": "Updated Title", "priority": "high"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["todo"]["title"], "Updated Title")
        self.assertEqual(data["todo"]["priority"], "high")

    def test_delete_todo(self):
        """Test deleting a todo."""
        create_resp = self._create_todo()
        todo_id = json.loads(create_resp.data)["todo"]["id"]
        response = self.client.delete("/api/todos/%d" % todo_id)
        self.assertEqual(response.status_code, 200)
        # Verify it's gone
        get_resp = self.client.get("/api/todos/%d" % todo_id)
        self.assertEqual(get_resp.status_code, 404)

    def test_complete_todo(self):
        """Test marking a todo as complete."""
        create_resp = self._create_todo()
        todo_id = json.loads(create_resp.data)["todo"]["id"]
        response = self.client.post("/api/todos/%d/complete" % todo_id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["todo"]["done"], True)

    def test_search_todos(self):
        """Test searching todos."""
        self._create_todo(title="Buy groceries")
        self._create_todo(title="Walk the dog")
        response = self.client.get("/api/todos/search?q=groceries")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["todos"]), 1)
        self.assertEqual(data["todos"][0]["title"], "Buy groceries")

    def test_todo_stats(self):
        """Test getting todo statistics."""
        self._create_todo(title="Task 1")
        self._create_todo(title="Task 2")
        create_resp = self._create_todo(title="Task 3")
        todo_id = json.loads(create_resp.data)["todo"]["id"]
        self.client.post("/api/todos/%d/complete" % todo_id)

        response = self.client.get("/api/todos/stats")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["stats"]["total"], 3)
        self.assertEqual(data["stats"]["completed"], 1)
        self.assertEqual(data["stats"]["pending"], 2)

    def test_filter_done_todos(self):
        """Test filtering out completed todos."""
        self._create_todo(title="Done task")
        create_resp = self._create_todo(title="Pending task")
        done_resp = self._create_todo(title="Also done")
        # Complete the first and third
        todo_id_1 = json.loads(self.client.get("/api/todos").data)["todos"][-1]["id"]
        todo_id_3 = json.loads(done_resp.data)["todo"]["id"]
        self.client.post("/api/todos/%d/complete" % todo_id_1)
        self.client.post("/api/todos/%d/complete" % todo_id_3)

        response = self.client.get("/api/todos?show_done=false")
        data = json.loads(response.data)
        self.assertEqual(len(data["todos"]), 1)
        self.assertEqual(data["todos"][0]["title"], "Pending task")


if __name__ == "__main__":
    unittest.main()
