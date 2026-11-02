# Copyright (c) InfoMCopilot-KR. All rights reserved.

"""API routes for todo operations."""

from flask import Blueprint, current_app, request, jsonify
from todoapp.models import TodoModel

api = Blueprint("api", __name__)


def _todo_model():
    return TodoModel(current_app.config.get("DATABASE"))


@api.route("/todos", methods=["GET"])
def list_todos():
    """List all todos. Query param: ?show_done=false to hide completed."""
    show_done = request.args.get("show_done", "true").lower() != "false"
    todos = _todo_model().get_all(show_done=show_done)
    return jsonify({"todos": todos})


@api.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    """Get a single todo by ID."""
    todo = _todo_model().get_by_id(todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify({"todo": todo})


@api.route("/todos", methods=["POST"])
def create_todo():
    """Create a new todo. Expects JSON with title, optional description and priority."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request must be JSON"}), 400
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body must be an object"}), 400

    title = data.get("title", "")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400
    title = title.strip()

    description = data.get("description", "")
    priority = data.get("priority", "medium")

    try:
        todo = _todo_model().create(title, description, priority)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"todo": todo}), 201


@api.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    """Update a todo. Accepts JSON with title, description, priority, done."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request must be JSON"}), 400
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body must be an object"}), 400

    try:
        todo = _todo_model().update(todo_id, **data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    return jsonify({"todo": todo})


@api.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """Delete a todo by ID."""
    deleted = _todo_model().delete(todo_id)
    if not deleted:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify({"message": "Todo deleted successfully"})


@api.route("/todos/<int:todo_id>/complete", methods=["POST"])
def complete_todo(todo_id):
    """Mark a todo as complete."""
    todo = _todo_model().update(todo_id, done=True)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify({"todo": todo})


@api.route("/todos/search", methods=["GET"])
def search_todos():
    """Search todos by query string. Query param: ?q=search_term"""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    todos = _todo_model().search(query)
    return jsonify({"todos": todos})


@api.route("/todos/stats", methods=["GET"])
def todo_stats():
    """Return todo statistics."""
    stats = _todo_model().count()
    stats["pending"] = stats["total"] - stats["completed"]
    return jsonify({"stats": stats})
