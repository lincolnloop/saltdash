FROM ipmb/ubuntu-python-platter:latest as build
ENV LANG C.UTF-8

ADD . /code

RUN /build.sh /code

FROM ipmb/ubuntu-python-clean:latest
RUN groupadd -r saltdash && useradd --uid=1000 --create-home --home-dir=/srv/saltdash --no-log-init -r -g saltdash saltdash
COPY --from=build /dist /dist

USER saltdash

RUN cd /tmp && tar xvzf /dist/saltdash-*.tar.gz --strip-components=1 && ./install.sh /srv/saltdash && mv data/setup.cfg /srv/saltdash && rm -rf /tmp/*

ENV PATH="/srv/saltdash/bin:${PATH}"
ENV WORKERS=4

WORKDIR /srv/saltdash

# Run tests with `pytest --cov`
CMD gunicorn -w ${WORKERS} -b 0.0.0.0:8000 saltdash.wsgi:application
