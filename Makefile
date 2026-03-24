.PHONY: up down build logs seed migrate shell

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f api

seed:
	docker compose exec -T postgres psql -U cluser -d collaborative_learning -f /init/seed.sql

migrate:
	docker compose exec api alembic upgrade head

shell:
	docker compose exec api bash
