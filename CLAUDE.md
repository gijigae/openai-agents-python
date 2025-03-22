# OpenAI Agents Python Library Assistance Guidelines

## Commands
- Lint: `make lint` (ruff)
- Format: `make format` (ruff format)
- Type check: `make mypy`
- Run tests: `make tests`
- Run single test: `uv run pytest tests/test_file.py::test_name`
- Build docs: `make build-docs`
- Serve docs locally: `make serve-docs`

## Code Style
- Python 3.9+ compatibility
- Line length: 100 characters
- Use snake_case for variables/functions, PascalCase for classes
- Imports: standard library → third-party → local modules
- Docstrings: Google style with Args/Returns/Raises sections
- Type hints required throughout (with TYPE_CHECKING conditional imports)
- Use dataclasses for data containers
- Custom exceptions inherit from AgentsException
- Comprehensive error handling with specific exception types
- Async/await patterns for asynchronous operations

## Library Architecture
- src/agents: Core library functionality
- Agent-based architecture with tools, guardrails, and handoffs
- Separate model interfaces (primarily OpenAI)
- Tracing infrastructure for debugging and monitoring