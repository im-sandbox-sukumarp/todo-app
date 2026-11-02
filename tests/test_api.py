# Copyright (c) InfoMCopilot-KR. All rights reserved.

"""Tests for the Todo List Manager API and web page."""

import json
import os
import tempfile
import unittest
from unittest import mock

from todoapp.app import create_app
from todoapp.database import drop_db, get_connection, get_db_path, init_db
from todoapp.models import TodoModel


class TodoApiTestCase(unittest.TestCase):
    """Test cases for the Todo API endpoints and web page."""

    api_prefix = "/api/v1"

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        self.app = create_app("testing")
        self.app.config["DATABASE"] = self.db_path
        init_db(self.db_path)
        self.client = self.app.test_client()

    def tearDown(self):
        drop_db(self.db_path)
        os.remove(self.db_path)

    def _create_todo(
        self,
        title="Test Todo",
        description="Test Description",
        priority="medium",
        prefix=None,
    ):
        prefix = prefix or self.api_prefix
        return self.client.post(
            prefix + "/todos",
            data=json.dumps({
                "title": title,
                "description": description,
                "priority": priority,
            }),
            content_type="application/json",
        )

    def _todo_id(self, response):
        return response.get_json()["todo"]["id"]

    def test_index_renders_github_themed_app(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"text/html", response.content_type.encode("ascii"))
        self.assertIn(b'id="todo-form"', response.data)
        self.assertIn(b"/static/css/app.css", response.data)
        stylesheet = self.client.get("/static/css/app.css")
        self.assertIn(b"#24292f", stylesheet.data)
        stylesheet.close()

    def test_create_app_uses_environment_default(self):
        with mock.patch.dict(os.environ, {"FLASK_ENV": "testing"}):
            app = create_app()
        self.assertTrue(app.config["TESTING"])

    def test_api_is_available_at_versioned_and_legacy_paths(self):
        for prefix in ("/api/v1", "/api"):
            with self.subTest(prefix=prefix):
                response = self.client.get(prefix + "/todos")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), {"todos": []})

    def test_not_found_handler_returns_json(self):
        response = self.client.get("/not-a-route")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Not found"})

    def test_internal_error_handler_returns_json(self):
        self.app.config["PROPAGATE_EXCEPTIONS"] = False

        def fail():
            raise RuntimeError("test error")

        self.app.add_url_rule("/test-error", view_func=fail)
        with self.assertLogs(self.app.logger.name, level="ERROR"):
            response = self.client.get("/test-error")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "Internal server error"})

    def test_create_todo(self):
        response = self._create_todo(title="  Test Todo  ")
        self.assertEqual(response.status_code, 201)
        todo = response.get_json()["todo"]
        self.assertEqual(todo["title"], "Test Todo")
        self.assertEqual(todo["priority"], "medium")
        self.assertFalse(todo["done"])

    def test_create_todo_without_title(self):
        response = self.client.post(
            self.api_prefix + "/todos",
            json={"description": "No title"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Title is required")

    def test_create_todo_rejects_non_string_title(self):
        response = self.client.post(self.api_prefix + "/todos", json={"title": 42})
        self.assertEqual(response.status_code, 400)

    def test_create_todo_requires_json(self):
        response = self.client.post(self.api_prefix + "/todos", data="title=Task")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Request must be JSON")

    def test_create_todo_rejects_non_object_json(self):
        response = self.client.post(self.api_prefix + "/todos", json=["Task"])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "JSON body must be an object")

    def test_create_todo_invalid_priority(self):
        response = self._create_todo(priority="urgent")
        self.assertEqual(response.status_code, 400)

    def test_list_todos(self):
        self._create_todo(title="First")
        self._create_todo(title="Second")
        response = self.client.get(self.api_prefix + "/todos")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["todos"]), 2)

    def test_list_todos_hides_completed(self):
        first_id = self._todo_id(self._create_todo(title="Completed"))
        self.client.post("%s/todos/%d/complete" % (self.api_prefix, first_id))
        self._create_todo(title="Open")
        response = self.client.get(self.api_prefix + "/todos?show_done=false")
        self.assertEqual([todo["title"] for todo in response.get_json()["todos"]], ["Open"])

    def test_get_todo(self):
        todo_id = self._todo_id(self._create_todo())
        response = self.client.get("%s/todos/%d" % (self.api_prefix, todo_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["todo"]["title"], "Test Todo")

    def test_get_nonexistent_todo(self):
        response = self.client.get(self.api_prefix + "/todos/9999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"], "Todo not found")

    def test_update_todo(self):
        todo_id = self._todo_id(self._create_todo())
        response = self.client.put(
            "%s/todos/%d" % (self.api_prefix, todo_id),
            json={"title": "Updated Title", "priority": "high"},
        )
        self.assertEqual(response.status_code, 200)
        todo = response.get_json()["todo"]
        self.assertEqual(todo["title"], "Updated Title")
        self.assertEqual(todo["priority"], "high")

    def test_update_todo_with_empty_or_unsupported_fields(self):
        todo_id = self._todo_id(self._create_todo(title="Keep title"))
        response = self.client.put(
            "%s/todos/%d" % (self.api_prefix, todo_id),
            json={"created_at": "not editable"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["todo"]["title"], "Keep title")

    def test_update_todo_rejects_invalid_priority(self):
        todo_id = self._todo_id(self._create_todo())
        response = self.client.put(
            "%s/todos/%d" % (self.api_prefix, todo_id),
            json={"priority": "urgent"},
        )
        self.assertEqual(response.status_code, 400)

    def test_update_todo_requires_json_object(self):
        todo_id = self._todo_id(self._create_todo())
        response = self.client.put(
            "%s/todos/%d" % (self.api_prefix, todo_id),
            data="not json",
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.put(
            "%s/todos/%d" % (self.api_prefix, todo_id),
            json=["not", "an", "object"],
        )
        self.assertEqual(response.status_code, 400)

    def test_update_nonexistent_todo(self):
        response = self.client.put(
            self.api_prefix + "/todos/9999",
            json={"title": "Missing"},
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_todo(self):
        todo_id = self._todo_id(self._create_todo())
        response = self.client.delete("%s/todos/%d" % (self.api_prefix, todo_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Todo deleted successfully")
        self.assertEqual(
            self.client.get("%s/todos/%d" % (self.api_prefix, todo_id)).status_code,
            404,
        )

    def test_delete_nonexistent_todo(self):
        response = self.client.delete(self.api_prefix + "/todos/9999")
        self.assertEqual(response.status_code, 404)

    def test_complete_todo(self):
        todo_id = self._todo_id(self._create_todo())
        response = self.client.post(
            "%s/todos/%d/complete" % (self.api_prefix, todo_id)
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["todo"]["done"])

    def test_complete_nonexistent_todo(self):
        response = self.client.post(self.api_prefix + "/todos/9999/complete")
        self.assertEqual(response.status_code, 404)

    def test_search_todos_by_title_and_description(self):
        self._create_todo(title="Buy groceries", description="Fruit and bread")
        self._create_todo(title="Walk the dog", description="Evening groceries run")
        title_response = self.client.get(self.api_prefix + "/todos/search?q=Buy")
        description_response = self.client.get(
            self.api_prefix + "/todos/search?q=Evening"
        )
        self.assertEqual(len(title_response.get_json()["todos"]), 1)
        self.assertEqual(len(description_response.get_json()["todos"]), 1)

    def test_search_requires_query(self):
        response = self.client.get(self.api_prefix + "/todos/search?q=%20%20")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Search query is required")

    def test_todo_stats(self):
        self._create_todo(title="Open")
        completed_id = self._todo_id(self._create_todo(title="Done"))
        self.client.post("%s/todos/%d/complete" % (self.api_prefix, completed_id))
        stats = self.client.get(self.api_prefix + "/todos/stats").get_json()["stats"]
        self.assertEqual(stats, {"total": 2, "completed": 1, "pending": 1})

    def test_todo_stats_for_empty_list(self):
        stats = self.client.get(self.api_prefix + "/todos/stats").get_json()["stats"]
        self.assertEqual(stats, {"total": 0, "completed": 0, "pending": 0})

    def test_model_converts_missing_row_to_none(self):
        self.assertIsNone(TodoModel(self.db_path)._row_to_dict(None))

    def test_database_helpers_use_environment_configuration(self):
        with mock.patch.dict(os.environ, {"FLASK_ENV": "testing"}):
            self.assertEqual(get_db_path(), ":memory:")
            connection = get_connection()
            self.assertIsNotNone(connection.row_factory)
            connection.close()
            init_db()
            drop_db()


if __name__ == "__main__":
    unittest.main()
