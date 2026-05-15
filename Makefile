.PHONY: dev-up dev-run dev-down db-ui-up db-up-down

dev-up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d postgres adminer app-dev

dev-run:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec app-dev cofepris run

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

db-ui-up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres adminer

db-up-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down
