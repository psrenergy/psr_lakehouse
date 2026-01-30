.PHONY: lint test docker_run

lint:
	uv sync
	uv run ruff check . --fix
	uv run ruff format .	

test:
	uv run pytest tests/unit/ -v -s

publish:
	uv sync
	uv build
	uv publish
