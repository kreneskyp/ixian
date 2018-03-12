FROM ubuntu:artful-20180123
ENV PROJECT_NAME power_shovel_tests

# =============================================================================
# Platform Installation
# =============================================================================

# Required packages
RUN apt-get update --fix-missing && \
    apt-get install -y \
        postgresql-client \
        git \
        python3 \
        python3-pip
RUN pip3 install pipenv

# Project directories
ENV APP_DIR /srv/$PROJECT_NAME
ENV PROJECT_DIR $APP_DIR/project
ENV VAR_DIR /var/run/$PROJECT_NAME
ENV ROOT_MODULE $PROJECT_NAME
ENV SRC_ROOT $PROJECT_DIR/$ROOT_MODULE
RUN mkdir -p $VAR_DIR && chown -R daemon $VAR_DIR
RUN mkdir $APP_DIR
WORKDIR $APP_DIR

# Source root of project
RUN mkdir -p $APP_DIR
RUN mkdir -p $PROJECT_DIR
RUN mkdir -p SRC_ROOT
ADD $ROOT_MODULE $SRC_ROOT

# Python - use Pipenv to control virtualenv
ENV PYTHON_VIRTUAL_ENV $APP_DIR/.venv
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8s
ENV PIPENV_SHELL_FANCY 1
ENV PIPENV_VENV_IN_PROJECT 1
ENTRYPOINT ["pipenv", "run"]


# =============================================================================
# Environment
# =============================================================================
USER root
#USER daemon
ADD .env $APP_DIR/
