#!/bin/bash
set -exu

cd $SOURCE_DIR/client
yarn install --production

# Setup project so we can collectstatic
pip install -e $SOURCE_DIR
export SECRET_KEY=none
export ALLOWED_HOSTS=none
manage.py collectstatic --noinput

# mv $SOURCE_DIR/static $DATA_DIR
#
#
# cat << "EOF" >> "$INSTALL_SCRIPT"
# MOD_PATH=$($VIRTUAL_ENV/bin/python -c "import os, saltdash; print(os.path.dirname(saltdash.__file__))")
# mv $DATA_DIR/static $MOD_PATH
# EOF
