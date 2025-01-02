#!/bin/bash
docker exec -w /app -e PYTHONPATH=/app server-container-credgem python scripts/load_seed_data.py --clear
