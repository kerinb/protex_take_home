DOCKER_IMAGE_NAME := cv_data_gen

# Docker build target
build:
	@docker build -t ${DOCKER_IMAGE_NAME} .

# Docker run target
run:
	@docker run ${DOCKER_IMAGE_NAME}

# Detect OS and shell for venv activation and python executable
UNAME_S := $(shell uname -s)
VENV_PYTHON = venv/bin/python3


ifeq ($(OS),Windows_NT)
    ACTIVATE = venv\Scripts\activate.bat
    PYTHON = python
	VENV_PYTHON = venv\Scripts\python.exe
    ACTIVATE_CMD = cmd /c "$(ACTIVATE) &&"
else ifeq ($(UNAME_S),Linux)
    ACTIVATE = source venv/bin/activate
    PYTHON = python3
    ACTIVATE_CMD = /bin/bash -c
else ifeq ($(UNAME_S),Darwin)
    ACTIVATE = source venv/bin/activate
    PYTHON = python3
    ACTIVATE_CMD = /bin/bash -c
else
    ACTIVATE = source venv/bin/activate
    PYTHON = python3
    ACTIVATE_CMD = /bin/bash -c
endif

venv:
	python -m venv venv
ifeq ($(OS),Windows_NT)
	venv\Scripts\python.exe -m pip install --upgrade pip
	venv\Scripts\python.exe -m pip install -r requirements/base.txt
	venv\Scripts\python.exe -m pip install -r requirements/test.txt
else
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/python3 -m pip install -r requirements/base.txt
	venv/bin/python3 -m pip install -r requirements/test.txt
endif



test:
	$(VENV_PYTHON) -m coverage run -m pytest


# Clean docker images and containers
clean-docker:
	@echo "Starting clean up of docker resources"
	@echo "Stopping and removing docker container ${DOCKER_IMAGE_NAME}"
	@docker stop ${DOCKER_IMAGE_NAME} || echo "Container ${DOCKER_IMAGE_NAME} could not be stopped or may not exist"
	@docker rm ${DOCKER_IMAGE_NAME} || echo "Container ${DOCKER_IMAGE_NAME} could not be removed or may not exist"
	@echo "Removing docker image ${DOCKER_IMAGE_NAME}"
	@docker rmi ${DOCKER_IMAGE_NAME} || echo "Image ${DOCKER_IMAGE_NAME} could not be removed or may not exist"
	@echo "Removing any dangling images"
	@docker image prune -f
	@echo "Docker cleanup complete"

# Convenience target: build, run, then cleanup
end-2-end: venv test build run
