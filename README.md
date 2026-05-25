# Todo List Manager API

A RESTful Todo List Manager built with Flask and SQLite.

## Features

- Create, read, update, and delete todos
- Priority levels (low, medium, high)
- Mark todos as complete
- Search todos by title or description
- Filter completed/pending todos
- Todo statistics endpoint

## Requirements

- Python 3.8+
- Flask 1.1.4

## Installation

```bash
# Install dependencies
make install

# Or manually
pip install -r requirements.txt
```

## Running the Application

```bash
make run

# Or manually
python run.py
```

The API server starts at `http://127.0.0.1:5000/`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and available endpoints |
| GET | `/api/todos` | List all todos |
| GET | `/api/todos?show_done=false` | List only pending todos |
| GET | `/api/todos/<id>` | Get a single todo |
| POST | `/api/todos` | Create a new todo |
| PUT | `/api/todos/<id>` | Update a todo |
| DELETE | `/api/todos/<id>` | Delete a todo |
| POST | `/api/todos/<id>/complete` | Mark a todo as complete |
| GET | `/api/todos/search?q=<query>` | Search todos |
| GET | `/api/todos/stats` | Get todo statistics |

### Create a Todo

```bash
curl -X POST http://127.0.0.1:5000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread", "priority": "high"}'
```

**Request body:**
- `title` (required): The todo title
- `description` (optional): Additional details
- `priority` (optional): One of `low`, `medium`, `high` (default: `medium`)

### Update a Todo

```bash
curl -X PUT http://127.0.0.1:5000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "done": true}'
```

**Request body (all fields optional):**
- `title`: New title
- `description`: New description
- `priority`: New priority level
- `done`: Boolean to mark as complete/incomplete

### Search Todos

```bash
curl http://127.0.0.1:5000/api/todos/search?q=groceries
```

## Running Tests

```bash
make test

# Or manually
python -m pytest tests/ -v
```

## Project Structure

```
todo-app/
├── config.py          # Application configuration
├── run.py             # Application entry point
├── Makefile           # Build and run commands
├── requirements.txt   # Python dependencies
├── setup.py           # Package setup
├── todoapp/
│   ├── __init__.py    # Package init
│   ├── app.py         # Flask application factory
│   ├── database.py    # Database initialization and connections
│   ├── models.py      # TodoModel with CRUD operations
│   └── routes.py      # API route handlers
└── tests/
    ├── __init__.py    # Test package init
    ├── test_api.py    # API endpoint tests
    ├── test_database.py  # Database utility tests
    ├── test_edge_cases.py # API edge case tests
    └── test_models.py # TodoModel unit tests
```

## Configuration

The application supports multiple configurations via the `FLASK_ENV` environment variable:

- `development` (default): Debug mode enabled, file-based SQLite database
- `testing`: Uses a temporary database file for tests
- `production`: Debug mode disabled
