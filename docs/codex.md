# Architecture

main.py defines a minimal FastAPI app exposing POST /items/ that forwards incoming message text to agent_service.agent.
agent_service.py configures a Gemini client with function-calling tools for task CRUD operations. It loops: (1) ask Gemini for a function call, (2) dispatch to a local function from todo_service, (3) feed the result back to Gemini for a natural-language reply. Note: update_task is declared as a tool but not wired in FUNCTIONS, so Gemini calls to update_task would currently fail to dispatch.
todo_service.py is an in-memory task store backed by the Task dataclass-like object. It keeps a module-level list _tasks, adds tasks, updates/deletes by code, and filters tasks by status/type/date (string comparisons).
task.py defines Task with auto-incrementing string codes, basic fields, and to_dict for serialization; state is held only in memory, no persistence across runs.
pyproject.toml lists runtime deps (python-dotenv) and now an optional dev extras group for pytest; runtime deps for FastAPI and google-genai are not yet declared, so installing them is required before running the API.
### Changes made

Added pytest suite covering task creation, updates, deletions, and filtering logic: tests/test_todo_service.py.
Added optional dev dependency for pytest in pyproject.toml to make test installs straightforward.
### Tests

Not run successfully: pytest is not available in the sandboxed environment (pip could not download packages). After installing deps (e.g., pip install -e .[dev] plus FastAPI/google-genai), run python -m pytest.


