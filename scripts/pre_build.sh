#!/bin/bash
# Collectstatic to include in package
set -exu

cd $SOURCE_DIR/client
yarn install --production

# Setup project so we can collectstatic
cd $SOURCE_DIR
pipenv install --deploy
echo "SECRET_KEY=secret" > .env
pipenv run manage.py collectstatic --noinput
