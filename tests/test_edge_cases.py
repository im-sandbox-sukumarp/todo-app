# -*- coding: utf-8 -*-

"""Additional API edge case tests for improved coverage."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from todoapp.app import create_app
from todoapp.database import init_db, drop_db


class TodoApiEdgeCaseTestCase(unittest.TestCase):
    """Test cases for API edge cases and error handling."""

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
        db_path = self.app.config["DATABASE"]
        if os.path.exists(db_path):
            os.remove(db_path)

    def _create_todo(self, title="Test Todo", description="", priority="medium"):
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

    def test_create_todo_not_json(self):
        """Test creating a todo with non-JSON content type."""
        response = self.client.post(
            "/api/todos",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_create_todo_empty_title(self):
        """Test creating a todo with empty string title."""
        response = self.client.post(
            "/api/todos",
            data=json.dumps({"title": "   "}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Title is required")

    def test_create_todo_with_all_priorities(self):
        """Test creating todos with each valid priority level."""
        for priority in ["low", "medium", "high"]:
            response = self._create_todo(title="Task %s" % priority, priority=priority)
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertEqual(data["todo"]["priority"], priority)

    def test_update_todo_not_json(self):
        """Test updating a todo with non-JSON content type."""
        resp = self._create_todo()
        todo_id = json.loads(resp.data)["todo"]["id"]
        response = self.client.put(
            "/api/todos/%d" % todo_id,
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_nonexistent_todo(self):
        """Test updating a todo that doesn't exist."""
        response = self.client.put(
            "/api/todos/9999",
            data=json.dumps({"title": "Updated"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_todo_invalid_priority(self):
        """Test updating a todo with an invalid priority."""
        resp = self._create_todo()
        todo_id = json.loads(resp.data)["todo"]["id"]
        response = self.client.put(
            "/api/todos/%d" % todo_id,
            data=json.dumps({"priority": "urgent"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_nonexistent_todo(self):
        """Test deleting a todo that doesn't exist."""
        response = self.client.delete("/api/todos/9999")
        self.assertEqual(response.status_code, 404)

    def test_complete_nonexistent_todo(self):
        """Test completing a todo that doesn't exist."""
        response = self.client.post("/api/todos/9999/complete")
        self.assertEqual(response.status_code, 404)

    def test_search_empty_query(self):
        """Test search with an empty query parameter."""
        response = self.client.get("/api/todos/search?q=")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Search query is required")

    def test_search_no_query_param(self):
        """Test search without the q parameter."""
        response = self.client.get("/api/todos/search")
        self.assertEqual(response.status_code, 400)

    def test_search_whitespace_query(self):
        """Test search with whitespace-only query."""
        response = self.client.get("/api/todos/search?q=   ")
        self.assertEqual(response.status_code, 400)

    def test_stats_empty_database(self):
        """Test stats endpoint with no todos."""
        response = self.client.get("/api/todos/stats")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["stats"]["total"], 0)
        self.assertEqual(data["stats"]["completed"], 0)
        self.assertEqual(data["stats"]["pending"], 0)

    def test_404_handler(self):
        """Test the 404 error handler for unknown routes."""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Not found")

    def test_index_contains_endpoints(self):
        """Test that the index endpoint lists all available endpoints."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("endpoints", data)
        self.assertIn("list_todos", data["endpoints"])
        self.assertIn("create_todo", data["endpoints"])
        self.assertIn("search_todos", data["endpoints"])
        self.assertIn("todo_stats", data["endpoints"])

    def test_list_todos_show_done_true(self):
        """Test listing all todos with show_done=true (default)."""
        resp = self._create_todo(title="Task")
        todo_id = json.loads(resp.data)["todo"]["id"]
        self.client.post("/api/todos/%d/complete" % todo_id)

        response = self.client.get("/api/todos?show_done=true")
        data = json.loads(response.data)
        self.assertEqual(len(data["todos"]), 1)

    def test_create_todo_with_description(self):
        """Test creating a todo with a description."""
        response = self._create_todo(title="Task", description="Details here")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["todo"]["description"], "Details here")


if __name__ == "__main__":
    unittest.main()
