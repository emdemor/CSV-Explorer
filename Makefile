-include .env

export

PROJECT_NAME := csv-explorer

JUPYTER_IMAGE := $(PROJECT_NAME)_jupyter
FRONT_IMAGE := $(PROJECT_NAME)_front

JUPYTER_DOCKERFILE_PATH := docker/Dockerfile.jupyter
FRONT_DOCKERFILE_PATH := docker/Dockerfile.frontend

JUPYTER_PORT ?= 8888
FRONT_PORT ?= 8501

DOCKER_RUN := docker run --rm -t
DOCKER_RUN_ITERACTIVE := $(DOCKER_RUN) -i
DOCKER_ENV := --env-file .env
DOCKER_COMPOSE := docker-compose -f $(DOCKER_COMPOSE_FILEPATH)

RUNNING_CONTAINERS = $(docker ps -a -q)

RUN_JUPYTER := $(DOCKER_RUN) $(DOCKER_ENV) -v ./notebooks:/project/notebooks -p $(JUPYTER_PORT):$(JUPYTER_PORT) $(JUPYTER_IMAGE)
RUN_FRONT := $(DOCKER_RUN) $(DOCKER_ENV) -v ./logs:/app/logs -p $(FRONT_PORT):$(FRONT_PORT) $(FRONT_IMAGE)

build: build-jupyter build-front

up:
	$(DOCKER_COMPOSE) up --build

down:
	$(DOCKER_COMPOSE) down

build-jupyter:
	docker build -f $(JUPYTER_DOCKERFILE_PATH) -t $(JUPYTER_IMAGE) .

run-jupyter:
	$(RUN_JUPYTER)

shell-jupyter:
	$(DOCKER_RUN_ITERACTIVE) $(DOCKER_ENV) -p $(JUPYTER_PORT):$(JUPYTER_PORT) $(JUPYTER_IMAGE) /bin/bash

build-front:
	docker build -f $(FRONT_DOCKERFILE_PATH) -t $(FRONT_IMAGE) .
	
front:
	$(RUN_FRONT)

shell-front:
	$(DOCKER_RUN_ITERACTIVE) $(DOCKER_ENV) -p $(FRONT_PORT):$(FRONT_PORT) $(FRONT_IMAGE) /bin/bash

update-vdb:
	dvc add database
	git add database.dvc .gitignore
	git commit -m "update database"

load-vdb:
	dvc pull

lrun:
	csv_explorer frontend start
