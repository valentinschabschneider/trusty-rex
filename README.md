<p align="center">
	<img src="docs/logo.png" alt="elliot logo" height="300px" style="margin-left: 4%;" />
</p>

# Trusty Rex

Docker image can be found on [Docker Hub](https://hub.docker.com/r/valentinschabschneider/trusty-rex).

## Development

```bash
uv run --env-file .env fastapi run --reload app/main.py
```

### Migrations

```bash
uv run --env-file .env alembic revision --autogenerate -m "Init"

uv run --env-file .env alembic upgrade head
```
