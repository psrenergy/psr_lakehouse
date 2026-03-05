.PHONY: lint test docker_run generate-aliases

lint:
	uv sync
	uv run ruff check . --fix
	uv run ruff format .	

test:
	uv run pytest tests/unit/ -v -s

generate-aliases:
	uv run python scripts/generate_aliases.py
	uv run ruff check src/psr/lakehouse/aliases.py --fix
	uv run ruff format src/psr/lakehouse/aliases.py

publish:
	uv sync
	uv build
	uv publish
