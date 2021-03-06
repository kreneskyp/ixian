FROM phusion/baseimage:0.11
ENV PROJECT_NAME ixian

# =============================================================================
# Platform Installation
# =============================================================================

# Required packages
RUN apt-get update --fix-missing && \
    apt-get upgrade -y && \
    install_clean \
        git \
        wget \
        curl \
        libbz2-dev \
        libffi-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools \
        build-essential \
        zlib1g-dev


# Project directories
ENV PROJECT_DIR /home/runner/work/ixian/$PROJECT_NAME
ENV SRC_ROOT $PROJECT_DIR/$PROJECT_NAME
ENV ROOT_MODULE $PROJECT_NAME

# Source root of project
ADD . $PROJECT_DIR

# Python
ENV PYENV_DIR=/home/runner/work/ixian/pyenv
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8s
RUN mkdir -p $PYENV_DIR
WORKDIR $PYENV_DIR

# install system python packages
RUN pip3 install -r $PROJECT_DIR/requirements-setup.txt
RUN pip3 install -r $PROJECT_DIR/requirements-dev.txt

# setup pyenv
ENV PYENV_3_6=3.6.10 \
    PYENV_3_7=3.7.7 \
    PYENV_3_8=3.8.2
ENV PYENV_VERSIONS "$PYENV_3_6 $PYENV_3_7 $PYENV_3_8"
ENV PATH "/root/.pyenv/bin:$PATH"
RUN curl https://pyenv.run | bash
RUN eval "$(pyenv init -)" \
 && eval "$(pyenv virtualenv-init -)"

# install python versions
RUN pyenv install $PYENV_3_6 \
 && pyenv install $PYENV_3_7 \
 && pyenv install $PYENV_3_8 \
 && pyenv local $PYENV_VERSIONS

WORKDIR $PROJECT_DIR