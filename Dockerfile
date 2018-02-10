FROM ubuntu:16.04 as build

ENV LANG C.UTF-8

# Install pre-requisites
RUN apt-get update && apt-get install -y curl apt-transport-https rsync software-properties-common build-essential git
RUN set -ex && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
    curl -sS https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    echo "deb https://deb.nodesource.com/node_8.x jessie main" > /etc/apt/sources.list.d/nodesource.list && \
    add-apt-repository ppa:deadsnakes/ppa && \
    curl -sOS https://bootstrap.pypa.io/get-pip.py
RUN apt-get update && apt-get install -y yarn python3.6 python3.6-dev && \
    python3.6 get-pip.py && pip3 install --upgrade pipenv && \
    python2 get-pip.py && pip2 install https://github.com/mitsuhiko/platter/archive/master.zip

# Add code
WORKDIR /srv/saltdash
ADD . /srv/saltdash

# Install dependencies, uWSGI, and build static assets
RUN set -ex && \
    sed -i 's/^\(version = .*\)$/\1+'$(git rev-parse HEAD)'/' setup.cfg && \
    platter build --prebuild-script=pre_build.sh -p python3.6 -r requirements.txt .


# Clean container
FROM ubuntu:16.04
RUN apt-get update && apt-get install -y software-properties-common && apt-add-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y python3.6

# Copy built packages from build stage (in production this would be S3)
COPY --from=build /srv/saltdash/dist/saltdash-*-linux-x86_64.tar.gz /

RUN cd /tmp && tar --strip-components=1 -xvzf saltdash-*-linux-x86_64.tar.gz && bash install.sh /srv/saltdash

WORKDIR /srv/saltdash

# Add virtualenv to PATH
ENV PATH="/srv/saltdash/bin:${PATH}"

