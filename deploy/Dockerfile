# One image, role chosen at runtime: MCP_ROLE=cop|thief (Track F).
FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && uv pip install --system --no-cache \
    pydantic numpy rich fastmcp python-dotenv
COPY config.json ./
COPY src ./src

ENV MCP_ROLE=cop
# platforms inject PORT; entrypoint maps it onto the role's configured port
COPY deploy/entrypoint.py ./deploy/entrypoint.py
CMD ["python", "deploy/entrypoint.py"]
