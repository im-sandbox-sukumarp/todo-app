# -*- coding: utf-8 -*-

"""Application configuration."""

import os


class Config(object):
    """Base configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.db")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_todos.db")


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
