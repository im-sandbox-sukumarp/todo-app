# -*- coding: utf-8 -*-

"""API routes for todo operations."""

from flask import Blueprint, request, jsonify, current_app
from todoapp.models import TodoModel

api = Blueprint("api", __name__, url_prefix="/api")


def _get_model():
    """Get a TodoModel instance configured with the current app's database."""
    db_path = current_app.config.get("DATABASE")
    return TodoModel(db_path)


@api.route("/todos", methods=["GET"])
def list_todos():
    """List all todos. Query param: ?show_done=false to hide completed."""
    show_done = request.args.get("show_done", "true").lower() != "false"
    todos = _get_model().get_all(show_done=show_done)
    return jsonify({"todos": todos})


@api.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    """Get a single todo by ID."""
    todo = _get_model().get_by_id(todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify({"todo": todo})


@api.route("/todos", methods=["POST"])
def create_todo():
    """Create a new todo. Expects JSON with title, optional description and priority."""
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request must be JSON"}), 400

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    description = data.get("description", "")
    priority = data.get("priority", "medium")

    try:
        todo = _get_model().create(title, description, priority)
    except ValueError as e:
        return jsonify({"error": "Invalid input: %s" % e.args[0] if e.args else "Invalid input"}), 400

    return jsonify({"todo": todo}), 201


@api.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    """Update a todo. Accepts JSON with title, description, priority, done."""
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request must be JSON"}), 400

    try:
        todo = _get_model().update(todo_id, **data)
    except ValueError as e:
        return jsonify({"error": "Invalid input: %s" % e.args[0] if e.args else "Invalid input"}), 400

    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    return jsonify({"todo": todo})


@api.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """Delete a todo by ID."""
    deleted = _get_model().delete(todo_id)
    if not deleted:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify({"message": "Todo deleted successfully"})


@api.route("/todos/<int:todo_id>/complete", methods=["POST"])
def complete_todo(todo_id):
    """Mark a todo as complete."""
    todo = _get_model().update(todo_id, done=True)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify({"todo": todo})


@api.route("/todos/search", methods=["GET"])
def search_todos():
    """Search todos by query string. Query param: ?q=search_term"""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    todos = _get_model().search(query)
    return jsonify({"todos": todos})


@api.route("/todos/stats", methods=["GET"])
def todo_stats():
    """Return todo statistics."""
    stats = _get_model().count()
    stats["pending"] = stats["total"] - stats["completed"]
    return jsonify({"stats": stats})
