rd /s /q ".pytest_cache"
rd /s /q ".ruff_cache"
rd /s /q ".venv"
rd /s /q "dist"

for /d /r %%d in (__pycache__) do (
    rd /s /q "%%d"
)

uv build
uv publish