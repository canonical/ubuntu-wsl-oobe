#
# Makefile for
#
NAME=ubuntu_wsl_oobe
PYTHONSRC=$(NAME)
PYTHONPATH=$(shell pwd)
export PYTHONPATH
CWD := $(shell pwd)

CHECK_DIRS := ubuntu_wsl_oobe/ subiquitycore/
PYTHON := python3

.PHONY: submcheck run clean check

all: dryrun

install_deps:
	sudo apt install -y python3-urwid python3-pyudev python3-nose python3-flake8 \
		python3-yaml python3-coverage python3-dev pkg-config libnl-genl-3-dev \
		libnl-route-3-dev python3-attr python3-distutils-extra python3-requests \
		python3-requests-unixsocket python3-jsonschema python3-curtin python3-apport \
		python3-bson

i18n:
	$(PYTHON) setup.py build_i18n
	cd po; intltool-update -r -g ubuntu_wsl_oobe

dryrun: i18n
	$(MAKE) ui-view DRYRUN="--dry-run"

ui-view:
	$(PYTHON) -m ubuntu_wsl_oobe.cmd.tui $(DRYRUN)

lint: flake8

flake8:
	@echo 'tox -e flake8' is preferred to 'make flake8'
	$(PYTHON) -m flake8 $(CHECK_DIRS) --exclude gettext38.py

unit:
	echo "Running unit tests..."
	$(PYTHON) -m nose $(CHECK_DIRS)

check: unit

submcheck:
	if [ ! -d "$(CMD)/external/subiquity" ]; then \
	echo "The git submodules are not available. Please run \`git submodule update --init --recursive\`"; \
	fi

clean:
	./debian/rules clean

.PHONY: flake8 lint
