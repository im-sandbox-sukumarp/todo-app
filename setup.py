# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="todo-app",
    version="1.0.0",
    description="A Todo List Manager built with Python 2 and Flask",
    author="Demo",
    packages=find_packages(),
    install_requires=[
        "Flask==1.1.4",
        "markupsafe==1.1.1",
        "itsdangerous==1.1.0",
        "Jinja2==2.11.3",
        "Werkzeug==1.0.1",
    ],
    python_requires=">=2.7, <3",
)
