# Makefile for LearnLab Docker operations

# Variables
DOCKER_REPO ?= learnlab # Default repository name - change if needed
TAG ?= latest           # Default tag
COMPOSE_FILE = docker-compose.yml
COMPOSE_FILE_PROD = docker-compose.prod.yml

# Define Docker services
SERVICES = frontend backend

# Top-level targets
.PHONY: help build up down down-clean start stop restart logs ps prod-up prod-down build-prod push-prod up-no-db fix-poetry fix-backend use-fixed-dockerfile

help:
	@echo "LearnLab Docker Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make build         - Build all Docker images"
	@echo "  make build-prod    - Build production Docker images"
	@echo "  make up            - Start all services in development mode"
	@echo "  make up-no-db      - Start all services except database"
	@echo "  make down          - Stop all services"
	@echo "  make down-clean    - Stop all services and remove volumes"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - View logs from all services"
	@echo "  make ps            - List running services"
	@echo "  make prod-up       - Start all services in production mode"
	@echo "  make prod-down     - Stop production services"
	@echo "  make push-prod     - Push production images to Docker Hub"
	@echo "  make fix-poetry    - Fix Poetry dependency issues by updating poetry.lock"
	@echo "  make fix-backend   - Fix backend Dockerfile to skip primp package"
	@echo "  make use-fixed-dockerfile - Use the fixed Dockerfile for the backend"
	@echo ""
	@echo "Service-specific commands:"
	@echo "  make build-frontend    - Build frontend image"
	@echo "  make build-backend     - Build backend image"
	@echo "  make logs-frontend     - View frontend logs"
	@echo "  make logs-backend      - View backend logs"
	@echo "  make restart-frontend  - Restart frontend service"
	@echo "  make restart-backend   - Restart backend service"

# Development environment commands
build:
	docker-compose -f $(COMPOSE_FILE) build

up:
	docker-compose -f $(COMPOSE_FILE) up -d

down:
	docker-compose -f $(COMPOSE_FILE) down

down-clean:
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans

start:
	docker-compose -f $(COMPOSE_FILE) start

stop:
	docker-compose -f $(COMPOSE_FILE) stop

restart:
	docker-compose -f $(COMPOSE_FILE) restart

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

ps:
	docker-compose -f $(COMPOSE_FILE) ps

# Run without database
up-no-db:
	docker-compose -f $(COMPOSE_FILE) up -d $(shell grep -v "db:" $(COMPOSE_FILE) | grep -v "depends_on:.*db" | grep "^\s*[a-zA-Z0-9_-]*:" | sed 's/:.*//g')

# Production environment commands
build-prod:
	docker-compose -f $(COMPOSE_FILE_PROD) build

prod-up:
	docker-compose -f $(COMPOSE_FILE_PROD) up -d

prod-down:
	docker-compose -f $(COMPOSE_FILE_PROD) down

# Push production images to Docker Hub
push-prod:
	@echo "Pushing production images to Docker Hub..."
	@for service in $(SERVICES); do \
		image_name=$$(grep -A1 "$$service:" $(COMPOSE_FILE_PROD) | grep "image:" | sed 's/image://g' | tr -d ' '); \
		if [ -n "$$image_name" ]; then \
			echo "Pushing $$image_name"; \
			docker push $$image_name; \
		else \
			echo "No image found for $$service"; \
		fi \
	done

# Service-specific commands
define make-service-targets
build-$(1):
	docker-compose -f $(COMPOSE_FILE) build $(1)

logs-$(1):
	docker-compose -f $(COMPOSE_FILE) logs -f $(1)

restart-$(1):
	docker-compose -f $(COMPOSE_FILE) restart $(1)
endef

$(foreach service,$(SERVICES),$(eval $(call make-service-targets,$(service))))
