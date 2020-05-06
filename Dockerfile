FROM node:8-alpine as build-node

WORKDIR /code
RUN apk --no-cache add make rsync bash
COPY Makefile ./
COPY client/package.json client/package-lock.json ./client/
RUN make client-install

COPY client/ ./client
RUN make client-build

FROM python:3.6 as build-python
ENV LANG C.UTF-8

ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /code
RUN pip3 install --user pipenv shiv
ADD . ./
COPY --from=build-node /code/client/dist/ ./client/dist
RUN set -ex && make setup && SECRET_KEY=s pipenv run saltdash collectstatic --noinput && make shiv

FROM python:3.6-slim
COPY --from=build-python /code/dist /dist
RUN groupadd -r saltdash && \
    useradd --uid=1000 --create-home --home-dir=/srv/saltdash --no-log-init -r -g saltdash saltdash && \
    ln -s /dist/*.pyz /bin/saltdash && chmod +x /dist/*.pyz

# Test reqs if you want that
COPY --from=build-python /code/setup.cfg /srv/saltdash/setup.cfg

USER saltdash

# Trigger shiv unpack
RUN SECRET_KEY=s /bin/saltdash help

WORKDIR /srv/saltdash
EXPOSE 8077
ENV LISTEN *:8077
VOLUME /etc/saltdash/
# Run tests with `pytest`
CMD /bin/saltdash serve
