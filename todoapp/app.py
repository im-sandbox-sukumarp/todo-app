# -*- coding: utf-8 -*-

"""Flask application factory."""

import os
from flask import Flask, jsonify
from config import config
from todoapp.database import init_db
from todoapp.routes import api


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize database
    init_db(app.config.get("DATABASE"))

    # Register blueprints
    app.register_blueprint(api)

    # Root endpoint
    @app.route("/")
    def index():
        return jsonify({
            "name": "Todo List Manager API",
            "version": "1.0.0",
            "endpoints": {
                "list_todos": "GET /api/todos",
                "get_todo": "GET /api/todos/<id>",
                "create_todo": "POST /api/todos",
                "update_todo": "PUT /api/todos/<id>",
                "delete_todo": "DELETE /api/todos/<id>",
                "complete_todo": "POST /api/todos/<id>/complete",
                "search_todos": "GET /api/todos/search?q=<query>",
                "todo_stats": "GET /api/todos/stats",
            }
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
