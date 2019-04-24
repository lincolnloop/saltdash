MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

client/node_modules: client/package.json client/yarn.lock
	cd client; NOYARNBUILD=1 yarn install --production

.PHONY: client-install
client-install: | client/node_modules

.PHONY: client-build
client-build: client-install
	cd client; yarn run build

saltdash/static: client-build
	SECRET_KEY=s poetry run saltdash collectstatic --noinput

# Make will use the log file to determine if it is newer than pyproject.lock
# and this should be rerun.
pyproject.log: pyproject.lock
	poetry install | tee $@

.PHONY: setup
setup: pyproject.log

saltdash.yml: setup
	poetry run saltdash-generate-config > $@

.PHONY: check
check: setup
	poetry run saltdash test

.PHONY: fmt
fmt:
	isort -m=3 --trailing-comma --line-width=88 --atomic $(shell find saltdash -name '*.py' -not -path "*/migrations/*")
	black $(shell find saltdash -name '*.py' -not -path "*/migrations/*")

version := $(shell python3 setup.py --version)
platform := $(shell python3 -c "import sysconfig as sc; print('py{}-{}'.format(sc.get_python_version().replace('.', ''), sc.get_platform()))")
sha := $(shell git rev-parse HEAD)

dist:
	mkdir $@

dist/saltdash-$(version)+$(sha)-$(platform).pyz: setup | dist
	shiv -e saltdash:config.django_manage -o $@ \
		 --site-packages=$(shell pipenv --venv)/lib/python3.6/site-packages \
		 --no-deps .

.PHONY: shiv
shiv: dist/saltdash-$(version)+$(sha)-$(platform).pyz

.PHONY: all
all: setup saltdash/static

.PHONY: release
release: clean all
	poetry run twine upload -s dist/*

.PHONY: clean
clean:
	rm -rf client/{node_modules,dist}
	rm -rf saltdash/static dist saltdash.egg-info pyproject.log
	#pipenv --venv && rm -rf $(shell pipenv --venv) || true
