DOCKER_IMAGE_NAME := cv_data_gen

# Docker build target
build:
	@docker build -t ${DOCKER_IMAGE_NAME} .

# Docker run target
run:
	@docker run ${DOCKER_IMAGE_NAME}

# Detect OS and shell for venv activation and python executable
UNAME_S := $(shell uname -s)
ifeq ($(OS),Windows_NT)
    ACTIVATE = venv\Scripts\activate.bat
    PYTHON = python
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

# Setup virtual environment and install requirements
venv:
	python -m venv venv
ifeq ($(OS),Windows_NT)
	cmd /c "venv\Scripts\activate.bat && pip install -r requirements/base.txt && pip install -r requirements/test.txt"
else
	/bin/bash -c "source venv/bin/activate && pip install -r requirements/base.txt && pip install -r requirements/test.txt"
endif

# Run tests inside the virtual environment with coverage
test:
ifeq ($(OS),Windows_NT)
	cmd /c "call venv\Scripts\activate.bat && python -m coverage run -m pytest"
else
	/bin/bash -c "source venv/bin/activate && python3 -m coverage run -m pytest"
endif

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
end-2-end: build run clean-docker
