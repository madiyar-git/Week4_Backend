.PHONY: help up down build restart migrate superuser shell logs ps clean-all

.DEFAULT_GOAL := help

help: ## Show all commands
	@echo "All commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start containers
	docker compose up -d

down: ## Stop and remove containers
	docker compose down

build: ## Rebuild project images
	docker compose build

restart: down up ## Restart containers (down + up)

migrate: ## Run Django database migrations
	docker compose exec web python manage.py migrate

superuser: ## Create Django superuser
	docker compose exec web python manage.py createsuperuser

shell: ## Open Django interactive shell
	docker compose exec web python manage.py shell

logs: ## View container logs in real time
	docker compose logs -f

ps: ## Display status of containers
	docker compose ps

clean-all: ## Remove containers, volumes (DB), and local images
	docker compose down -v --rmi local

test: ## Run tests with terminal coverage report
	docker compose exec web pytest --cov=. --cov-report=term-missing --reuse-db

test-html: ## Run tests and generate HTML coverage report
	docker compose exec web pytest --cov=. --cov-report=html --reuse-db

test-fast: ## Run tests in parallel without coverage
	docker compose exec web pytest -n auto --reuse-db