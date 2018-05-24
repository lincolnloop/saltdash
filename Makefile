MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

client/node_modules: client/package.json client/yarn.lock
	cd client; NOYARNBUILD=1 yarn install --production

.PHONY: client-install
## Install static file dependencies
client-install: | client/node_modules

.PHONY: client-build
## Build static files
client-build: client-install
	cd client; yarn run build

saltdash/static: client-build
	SECRET_KEY=s pipenv run saltdash collectstatic --noinput

.PHONY: static
## Collect static files for distribution
static: saltdash/static

# Make will use the log file to determine if it is newer than Pipfile.lock
# and this should be rerun.
Pipfile.log: Pipfile.lock
	pipenv install --deploy | tee $@

.PHONY: setup
## Install Python dependencies
setup: Pipfile.log


saltdash.yml: setup
	pipenv run saltdash-generate-config > $@

.PHONY: config
## Generate config
config: saltdash.yml

.PHONY: check
## Run tests
check: setup
	pipenv run saltdash test

.PHONY: fmt
## Format Python with Black
fmt:
	black $(shell find saltdash -name '*.py' -not -path "*/migrations/*")

version := $(shell python3 setup.py --version)
platform := $(shell python3 -c "import sysconfig as sc; print('py{}-{}'.format(sc.get_python_version().replace('.', ''), sc.get_platform()))")
sha := $(shell git rev-parse HEAD)

dist:
	mkdir $@

dist/saltdash-$(version)+$(sha)-$(platform).pyz: all saltdash/libuwsgi.so | dist
	shiv -e saltdash:config.django_manage -o $@ .

.PHONY: shiv
## Build a shiv for the project in the `dist` directory
shiv: dist/saltdash-$(version)+$(sha)-$(platform).pyz

saltdash/libuwsgi.so:
	UWSGI_AS_LIB=$(shell pwd)/$@ UWSGI_EMBED_PLUGINS=stats_pusher_statsd pip install --no-cache-dir --ignore-installed uwsgi

.PHONY: uwsgi
## Install uWSGI as a library for use with `saltdash uwsgi`
uwsgi: saltdash/libuwsgi.so

.PHONY: all
## Full project install
all: setup saltdash/static

.PHONY: release
release: clean all
	pipenv run twine upload -s dist/*

.PHONY: clean
## Remove all generated files
clean:
	rm -rf client/{node_modules,dist}
	rm -rf saltdash/static dist build saltdash.egg-info Pipfile.log
	rm -f saltdash/libuwsgi.so
	pipenv --venv && rm -rf $(shell pipenv --venv) || true



# Adds a help command to list and document the different targets
# via https://gist.github.com/prwhite/8168133#gistcomment-2278355

GREEN  := $(shell tput -Txterm setaf 2)
RESET  := $(shell tput -Txterm sgr0)
TARGET_MAX_CHAR_NUM=20
.PHONY: help
## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  make ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9.\/]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${GREEN}%-$(TARGET_MAX_CHAR_NUM)s${RESET} %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
