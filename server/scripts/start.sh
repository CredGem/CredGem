#!/bin/bash

# Run migrations
poetry run alembic upgrade head

# Start the application
exec python -m src 