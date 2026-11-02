#!/usr/bin/env python
# Copyright (c) InfoMCopilot-KR. All rights reserved.

"""Entry point for the Todo List Manager application."""

from todoapp.app import create_app

app = create_app()

if __name__ == "__main__":
    print("Starting Todo List Manager...")
    print("Running on http://127.0.0.1:5000/")
    app.run(host="0.0.0.0", port=5000, debug=True)
