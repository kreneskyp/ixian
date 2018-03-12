#!/bin/sh

# pushd $PROJECT_DIR
pushd /srv/power_shovel_tests/project
nosetests $@
popd
