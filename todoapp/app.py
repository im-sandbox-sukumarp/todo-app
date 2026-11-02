# Copyright (c) InfoMCopilot-KR. All rights reserved.

"""Flask application factory."""

import os
from flask import Flask, jsonify, render_template
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

    # Keep the original API path available while exposing the versioned API.
    app.register_blueprint(api, url_prefix="/api/v1")
    app.register_blueprint(api, url_prefix="/api", name="api_legacy")

    @app.route("/")
    def index():
        return render_template("index.html")

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
