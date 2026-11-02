// Copyright (c) InfoMCopilot-KR. All rights reserved.
"use strict";

const API_URL = "/api/v1";
const todoForm = document.querySelector("#todo-form");
const todoList = document.querySelector("#todo-list");
const searchForm = document.querySelector("#search-form");
const searchInput = document.querySelector("#search-input");
const statusMessage = document.querySelector("#status-message");
const emptyState = document.querySelector("#empty-state");
const openCount = document.querySelector("#open-count");
const taskSummary = document.querySelector("#task-summary");
const completionSummary = document.querySelector("#completion-summary");
const filterButtons = document.querySelectorAll(".filter-tab");

let activeFilter = "open";

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "The request could not be completed.");
  }
  return payload;
}

function showError(message) {
  statusMessage.textContent = message;
  statusMessage.hidden = false;
}

function clearError() {
  statusMessage.textContent = "";
  statusMessage.hidden = true;
}

function createTodoRow(todo) {
  const row = document.createElement("li");
  row.className = `todo-row${todo.done ? " is-done" : ""}`;

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.className = "todo-checkbox";
  checkbox.checked = todo.done;
  checkbox.setAttribute("aria-label", `${todo.done ? "Reopen" : "Complete"} ${todo.title}`);
  checkbox.addEventListener("change", async () => {
    try {
      await requestJson(`/todos/${todo.id}`, {
        method: "PUT",
        body: JSON.stringify({ done: checkbox.checked }),
      });
      await loadTodos();
    } catch (error) {
      checkbox.checked = todo.done;
      showError(error.message);
    }
  });

  const main = document.createElement("div");
  main.className = "todo-main";
  const title = document.createElement("span");
  title.className = "todo-title";
  title.textContent = todo.title;
  main.append(title);

  if (todo.description) {
    const description = document.createElement("p");
    description.className = "todo-description";
    description.textContent = todo.description;
    main.append(description);
  }

  const meta = document.createElement("div");
  meta.className = "todo-meta";
  const priority = document.createElement("span");
  priority.className = `priority priority-${todo.priority}`;
  priority.textContent = `${todo.priority[0].toUpperCase()}${todo.priority.slice(1)} priority`;
  meta.append(priority);
  if (todo.done) {
    const doneLabel = document.createElement("span");
    doneLabel.className = "done-label";
    doneLabel.textContent = "Completed";
    meta.append(doneLabel);
  }
  main.append(meta);

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "delete-button";
  deleteButton.textContent = "Delete";
  deleteButton.setAttribute("aria-label", `Delete ${todo.title}`);
  deleteButton.addEventListener("click", async () => {
    try {
      await requestJson(`/todos/${todo.id}`, { method: "DELETE" });
      await loadTodos();
    } catch (error) {
      showError(error.message);
    }
  });

  row.append(checkbox, main, deleteButton);
  return row;
}

async function loadTodos() {
  clearError();
  taskSummary.textContent = "Loading your tasks…";
  try {
    const query = searchInput.value.trim();
    const searchPath = query ? `/todos/search?q=${encodeURIComponent(query)}` : null;
    const listPath = activeFilter === "open" && !query
      ? "/todos?show_done=false"
      : "/todos";
    const [todoPayload, statsPayload] = await Promise.all([
      requestJson(searchPath || listPath),
      requestJson("/todos/stats"),
    ]);

    const allTodos = todoPayload.todos;
    const visibleTodos = allTodos.filter((todo) => {
      if (activeFilter === "open") return !todo.done;
      if (activeFilter === "completed") return todo.done;
      return true;
    });

    todoList.replaceChildren(...visibleTodos.map(createTodoRow));
    emptyState.hidden = visibleTodos.length !== 0;
    openCount.textContent = String(statsPayload.stats.pending);
    taskSummary.textContent = `${visibleTodos.length} ${visibleTodos.length === 1 ? "task" : "tasks"}`;
    completionSummary.textContent =
      `${statsPayload.stats.completed} completed · ${statsPayload.stats.total} total`;
  } catch (error) {
    taskSummary.textContent = "Tasks could not be loaded.";
    showError(error.message);
  }
}

todoForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(todoForm);
  const task = {
    title: formData.get("title"),
    description: formData.get("description"),
    priority: formData.get("priority"),
  };
  try {
    await requestJson("/todos", {
      method: "POST",
      body: JSON.stringify(task),
    });
    todoForm.reset();
    document.querySelector("#todo-priority").value = "medium";
    activeFilter = "open";
    filterButtons.forEach((button) => {
      const selected = button.dataset.filter === activeFilter;
      button.classList.toggle("active", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    await loadTodos();
  } catch (error) {
    showError(error.message);
  }
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    filterButtons.forEach((candidate) => {
      const selected = candidate === button;
      candidate.classList.toggle("active", selected);
      candidate.setAttribute("aria-pressed", String(selected));
    });
    loadTodos();
  });
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loadTodos();
});

searchInput.addEventListener("input", loadTodos);

loadTodos();
