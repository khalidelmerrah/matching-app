.PHONY: up down test fmt lint migrate help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start services (postgres, redis)
	docker-compose -f infra/docker-compose.yml up -d

down: ## Stop services
	docker-compose -f infra/docker-compose.yml down

test: ## Run backend tests
	cd backend && pytest

fmt: ## Run code formatters
	cd backend && ruff format . && black .

lint: ## Run linters
	cd backend && ruff check . && mypy .

migrate: ## Run database migrations
	cd backend && alembic upgrade head

makemigrations: ## Create new migration (usage: make makemigrations message="...")
	cd backend && alembic revision --autogenerate -m "$(message)"

smoke: ## Boot infra, migrate, and run tests
	$(MAKE) up
	@echo "Waiting for services to be healthy..."
	@timeout 10s bash -c 'until docker-compose -f infra/docker-compose.yml ps | grep "healthy" > /dev/null; do sleep 1; done' || echo "Services ready or check skipped"
	$(MAKE) migrate
	$(MAKE) test
