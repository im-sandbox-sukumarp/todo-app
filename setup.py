# Copyright (c) InfoMCopilot-KR. All rights reserved.

from setuptools import setup, find_packages

setup(
    name="todo-app",
    version="1.0.0",
    description="A GitHub-themed Todo List Manager built with Flask",
    author="InfoMCopilot-KR",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "todoapp": [
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
        ],
    },
    install_requires=[
        "Flask==3.1.1",
    ],
    python_requires=">=3.9",
)
