PROJECT_NAME=ixian
IMAGE=ixian_tests
PROJECT_DIR=/home/runner/work/ixian/${PROJECT_NAME}
DOCKER_RUN=docker run -it -v `pwd`:${PROJECT_DIR} ${IMAGE}
PYENV_DIR=/home/runner/work/ixian/pyenv


.image_created: Dockerfile requirements*.txt
	docker build -f Dockerfile -t ${IMAGE} .
	touch $@


.python_version:
	${DOCKER_RUN} cp ${PYENV_DIR}/.python-version ${PROJECT_DIR}


.PHONY: test
test: .image_created .python_version
	${DOCKER_RUN} tox -v


.PHONY: black
black: .image_created .python_version
	${DOCKER_RUN} black .


.PHONY: black-check
black-check: .image_created .python_version
	${DOCKER_RUN} black --check .


.PHONY: bash
bash: .image_created .python_version
	${DOCKER_RUN} /bin/bash

.PHONY: dist
dist:
	${DOCKER_RUN} python3 setup.py sdist bdist_wheel

.PHONY: dist-check
dist-check:
	${DOCKER_RUN} twine check dist/*

.PHONY: docs
docs: docs/Makefile
	${DOCKER_RUN} tox -e docs

.PHONY: publish
publish:
	${DOCKER_RUN} twine upload dist/*

.PHONY: publish-test
publish-test:
	${DOCKER_RUN} twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: clean
clean:
	rm -rf .tox
	rm -rf .coverage
	rm -rf .eggs
	rm -rf dist
	rm -rf build

.PHONY: teardown
teardown: clean
	rm -rf .image_created
	rm -rf .python-version
