FROM python:3.6 as build
ENV LANG C.UTF-8

ENV PATH="/root/.local/bin:${PATH}"
RUN pip3 install --user pipenv https://github.com/lincolnloop/platter/archive/updates.zip
RUN set -ex && \
    apt-get update -q && apt-get install -y lsb-release apt-transport-https rsync && \
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
    curl -sS https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo "deb https://deb.nodesource.com/node_8.x $(lsb_release -s -c) main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update -q && apt-get install -y yarn nodejs
ADD . /code
RUN platter build --output=/dist /code

FROM python:3.6-slim
RUN groupadd -r saltdash && \
    useradd --uid=1000 --create-home --home-dir=/srv/saltdash --no-log-init -r -g saltdash saltdash
COPY --from=build /dist /dist

USER saltdash

RUN set -ex && cd /tmp && \
    tar xvzf /dist/saltdash-*.tar.gz --strip-components=1 && \
    ./install.sh /srv/saltdash && \
    mv data/setup.cfg /srv/saltdash && rm -rf /tmp/*

ENV PATH="/srv/saltdash/bin:${PATH}"

WORKDIR /srv/saltdash

# Run tests with `pytest`
CMD saltdash serve
