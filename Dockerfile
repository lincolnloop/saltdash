FROM python:3.6 as build
ENV LANG C.UTF-8

ENV PATH="/root/.local/bin:${PATH}"
RUN pip3 install --user pipenv shiv
RUN set -ex && \
    apt-get update -q && apt-get install -y lsb-release apt-transport-https rsync && \
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
    curl -sS https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo "deb https://deb.nodesource.com/node_8.x $(lsb_release -s -c) main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update -q && apt-get install -y yarn nodejs
ADD . /code
RUN cd /code && make shiv

FROM python:3.6-slim
COPY --from=build /code/dist /dist
RUN set -ex && \
    apt-get update -q && apt-get install -y --no-install-recommends mime-support libxml2 && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r saltdash && \
    useradd --uid=1000 --create-home --home-dir=/srv/saltdash --no-log-init -r -g saltdash saltdash && \
    ln -s /dist/*.pyz /bin/saltdash && chmod +x /dist/*.pyz

# Test reqs if you want that
COPY --from=build /code/setup.cfg /srv/saltdash/setup.cfg

USER saltdash

# Trigger shiv unpack
RUN SECRET_KEY=s /bin/saltdash help

WORKDIR /srv/saltdash
EXPOSE 8077
ENV LISTEN *:8077
VOLUME /etc/saltdash/
ENTRYPOINT ["/bin/saltdash"]
CMD ["serve"]
