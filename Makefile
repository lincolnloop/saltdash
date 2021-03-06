MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

client/node_modules: client/package.json client/package-lock.json
	cd client; NOBUILD=1 npm install --production

.PHONY: client-install
client-install: | client/node_modules

.PHONY: client-build
client-build: client-install
	cd client; npm run build

saltdash/static: client-build
	SECRET_KEY=s pipenv run saltdash collectstatic --noinput

# Make will use the log file to determine if it is newer than Pipfile.lock
# and this should be rerun.
Pipfile.log: Pipfile.lock
	pipenv install --deploy | tee $@

.PHONY: setup
setup: Pipfile.log

saltdash.yml: setup
	pipenv run saltdash-generate-config > $@

.PHONY: check
check: setup
	pipenv run saltdash test

.PHONY: fmt
fmt:
	isort -m=3 --trailing-comma --line-width=88 --atomic $(shell find saltdash -name '*.py' -not -path "*/migrations/*")
	black $(shell find saltdash -name '*.py' -not -path "*/migrations/*")

version := $(shell python3 setup.py --version)
platform := $(shell python3 -c "import sysconfig as sc; print('py{}-{}'.format(sc.get_python_version().replace('.', ''), sc.get_platform()))")
sha := $(shell git rev-parse HEAD)

dist:
	mkdir $@

dist/saltdash-$(version).tar.gz: dist
	python setup.py sdist

dist/saltdash-$(version)-py2.py3-none-any.whl: dist
	python setup.py bdist_wheel

dist/saltdash-$(version)+$(sha)-$(platform).pyz: setup | dist
	shiv -e saltdash:config.django_manage -o $@ \
		 --site-packages=$(shell pipenv --venv)/lib/python3.6/site-packages \
		 --no-deps .

.PHONY: shiv
shiv: dist/saltdash-$(version)+$(sha)-$(platform).pyz

.PHONY: all
all: setup saltdash/static

.PHONY: release
release: clean all dist/saltdash-$(version).tar.gz dist/saltdash-$(version)-py2.py3-none-any.whl
	pipenv run twine upload -s dist/*

.PHONY: clean
clean:
	rm -rf client/{node_modules,dist}
	rm -rf saltdash/static dist saltdash.egg-info Pipfile.log
	pipenv --rm || true
