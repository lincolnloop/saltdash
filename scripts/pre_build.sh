#!/bin/bash
# Collectstatic to include in package
set -exu

cd $SOURCE_DIR/client
yarn install --production

# Setup project so we can collectstatic
pip install -e $SOURCE_DIR
export SECRET_KEY=none
export ALLOWED_HOSTS=none
manage.py collectstatic --noinput
