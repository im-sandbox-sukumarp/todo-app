# Todo API

The current API version is **v1**. Use `/api/v1` for new clients. The original
`/api` path remains available for compatibility.

All request and response bodies use JSON. Todo records have an integer `id`, a
non-empty `title`, an optional `description`, a `priority` (`low`, `medium`, or
`high`), a boolean `done` value, and creation/update timestamps.

| Method | Versioned path | Purpose |
|---|---|---|
| `GET` | `/api/v1/todos` | List tasks. Use `?show_done=false` to hide completed tasks. |
| `GET` | `/api/v1/todos/<id>` | Get one task. |
| `POST` | `/api/v1/todos` | Create a task with `title`, optional `description`, and optional `priority`. |
| `PUT` | `/api/v1/todos/<id>` | Update `title`, `description`, `priority`, or `done`. |
| `DELETE` | `/api/v1/todos/<id>` | Delete one task. |
| `POST` | `/api/v1/todos/<id>/complete` | Mark one task complete. |
| `GET` | `/api/v1/todos/search?q=<query>` | Search task titles and descriptions. |
| `GET` | `/api/v1/todos/stats` | Get total, completed, and pending counts. |

Invalid requests return a JSON `error` field with status `400`; missing tasks
return status `404`. Create requests return status `201`.
