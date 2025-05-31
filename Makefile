DOCKER_IMAGE_NAME := cv_data_gen

build:
	@docker build -t ${DOCKER_IMAGE_NAME} .

run:
	@docker run  -e INPUT_PATH="different/input/path" ${DOCKER_IMAGE_NAME}

ifeq ($(OS),Windows_NT)
    ACTIVATE = .\venv\Scripts\activate
else
    ACTIVATE = . venv/bin/activate
endif

venv:
	python -m venv venv
	$(ACTIVATE)
	@pip install --no-cache-dir -r requirements/base.txt
	@pip install --no-cache-dir -r requirements/test.txt


test:
	. venv/bin/activate
	coveage run -m pytest

clean-docker:
	@echo "starting clean up of docker resources"
	@echo "Stopping and remove docker image"
	@docker stop ${DOCKER_IMAGE_NAME} || echo "Image ${DOCKER_IMAGE_NAME} could not be stopped, it may not be in use or may not exist"
	@docker rmi ${DOCKER_IMAGE_NAME} || echo "Image ${DOCKER_IMAGE_NAME} could not be removed, it may not be in use or may not exist"

	@echo "remove any other dangling images"
	@docker image prune -f
	@echo "Docker clean up complete"