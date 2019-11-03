PROJECT_NAME=power_shovel
IMAGE=chang_tests
PROJECT_DIR=/opt/${PROJECT_NAME}
DOCKER_RUN=docker run -it -v `pwd`:${PROJECT_DIR} ${IMAGE}
PYENV_DIR=/opt/pyenv


.image_created: Dockerfile requirements*.txt
	docker build -f Dockerfile -t ${IMAGE} .
	touch $@


.python_version:
	${DOCKER_RUN} cp ${PYENV_DIR}/.python-version ${PROJECT_DIR}


test: .image_created .python_version
	${DOCKER_RUN} tox


black: .image_created .python_version
	${DOCKER_RUN} black .


black-check: .image_created .python_version
	${DOCKER_RUN} black --check .


bash: .image_created .python_version
	${DOCKER_RUN} /bin/bash


