.PHONY: help up down build restart migrate superuser shell logs ps clean-all

.DEFAULT_GOAL := help

help:
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

restart: down up

migrate:
	docker compose exec web python manage.py migrate

superuser:
	docker compose exec web python manage.py createsuperuser

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f

ps:
	docker compose ps

clean-all:
	docker compose down -v --rmi local