# Copyright (c) InfoMCopilot-KR. All rights reserved.

"""Database initialization and connection management."""

import sqlite3
import os
from config import config


def get_db_path():
    """Return the database file path from config."""
    env = os.environ.get("FLASK_ENV", "development")
    cfg = config.get(env, config["default"])
    return cfg.DATABASE


def get_connection(db_path=None):
    """Create and return a database connection."""
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    """Initialize the database with the schema."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'medium',
            done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def drop_db(db_path=None):
    """Drop all tables."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS todos")
    conn.commit()
    conn.close()
