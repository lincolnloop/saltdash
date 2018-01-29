FROM python:3.6-stretch as build

ENV LANG C.UTF-8
ENV PIPENV_VENV_IN_PROJECT=true
# Temporary settings so collectstatic can run
ENV DJANGO_SETTINGS_MODULE=saltdash.settings SECRET_KEY=none ALLOWED_HOSTS=none

# Install pre-requisites
RUN apt-get update && apt-get install -y apt-transport-https rsync
RUN set -ex && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
    curl -sS https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo "deb https://deb.nodesource.com/node_8.x jessie main" > /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install -y yarn && pip3 install --upgrade pipenv

# Add code
WORKDIR /srv/saltdash
ADD . /srv/saltdash

# Install dependencies, uWSGI, and build static assets
RUN set -ex && pipenv install --deploy && pipenv run pip install -U uWSGI && \
    cd client && yarn --production && cd .. && pipenv run saltdash collectstatic --noinput && \
    rm -rf client/node_modules client/.cache


FROM python:3.6-slim-stretch
# Install libs for uWSGI and setup user
RUN apt-get update && apt-get install -y libxml2 mime-support && rm -rf /var/lib/apt/lists/* && \
    groupadd -r saltdash && useradd --uid=1000 --create-home --home-dir=/srv/saltdash --no-log-init -r -g saltdash saltdash

# Copy built packages from build stage
COPY --from=build --chown=saltdash:saltdash /srv/saltdash /srv/saltdash
WORKDIR /srv/saltdash
USER saltdash

# Add virtualenv to PATH
ENV PATH="/srv/saltdash/.venv/bin:${PATH}"

CMD uwsgi --ini=uwsgi.ini
