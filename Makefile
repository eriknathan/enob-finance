.PHONY: help build up down restart logs migrate makemigrations createsuperuser shell bash

# Default target
help:
	@echo "Comandos disponíveis:"
	@echo "  make up              - Inicia os containers em background"
	@echo "  make build           - Reconstrói a imagem e inicia os containers"
	@echo "  make down            - Para e remove os containers"
	@echo "  make restart         - Reinicia os containers"
	@echo "  make logs            - Mostra os logs dos containers em tempo real"
	@echo "  make migrate         - Executa as migrações do banco de dados no container"
	@echo "  make makemigrations  - Cria novas migrações baseadas nos modelos"
	@echo "  make createsuperuser - Cria um usuário administrador no Django"
	@echo "  make shell           - Abre o terminal interativo do Django (shell)"
	@echo "  make bash            - Abre o terminal (sh) dentro do container web"

build:
	docker compose up --build -d

up:
	@echo "Iniciando build e recriando containers..."
	docker compose up --build --force-recreate -d
	@echo "Aguardando os serviços iniciarem..."
	@sleep 3
	@echo "Gerando novas migrações (se houver)..."
	docker compose exec web python manage.py makemigrations
	@echo "Aplicando migrações no banco de dados..."
	docker compose exec web python manage.py migrate
	@echo "Ambiente 100% pronto e rodando!"

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

createsuperuser:
	docker compose exec web python manage.py createsuperuser

shell:
	docker compose exec web python manage.py shell

bash:
	docker compose exec web sh
