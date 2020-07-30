#
# Makefile for subiquity
#
NAME=ubuntu_wsl_oobe
PYTHONSRC=$(NAME)
PYTHONPATH=$(shell pwd):$(shell pwd)/external/probert
export PYTHONPATH
CWD := $(shell pwd)

CHECK_DIRS := ubuntu_wsl_oobe/ subiquitycore/
PYTHON := python3

ifneq (,$(MACHINE))
	MACHARGS=--machine=$(MACHINE)
endif

.PHONY: submcheck run clean check

all: dryrun

install_deps:
	sudo apt-get install -y python3-urwid python3-pyudev python3-nose python3-flake8 \
		python3-yaml python3-coverage python3-dev pkg-config libnl-genl-3-dev \
		libnl-route-3-dev python3-attr python3-distutils-extra python3-requests \
		python3-requests-unixsocket python3-jsonschema python3-curtin python3-apport \
		python3-bson

dryrun: probert
	$(MAKE) ui-view DRYRUN="--dry-run"

ui-view:
	$(PYTHON) -m ubuntu_wsl_oobe.cmd.tui $(DRYRUN) $(MACHARGS)

lint: flake8

flake8:
	@echo 'tox -e flake8' is preferred to 'make flake8'
	$(PYTHON) -m flake8 $(CHECK_DIRS) --exclude gettext38.py

unit:
	echo "Running unit tests..."
	$(PYTHON) -m nose $(CHECK_DIRS)

check: unit

submcheck:
	if [ ! -d "$(CMD)/external/probert" ] || [ ! -d "$(CMD)/external/subiquity" ]; then \
	echo "The git submodules are not available. Please run \`git submodule update --init --recursive\`"; \
	fi

probert:
	@if [ ! -d "$(PROBERTDIR)" ]; then \
		(cd external/probert && $(PYTHON) setup.py build_ext -i); \
    fi

clean:
	./debian/rules clean

.PHONY: flake8 lint
