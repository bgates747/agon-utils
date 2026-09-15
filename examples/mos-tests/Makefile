# Standard AgonDev integration. Run make from this subproject directory.
.DEFAULT_GOAL := all
NAME := mos-tests

# Explicit installation resolution also works in noninteractive SSH shells.
AGONDEV_TOOLCHAIN ?= /home/smith/Agon/agondev/release
AGONDEV_CONFIG := $(AGONDEV_TOOLCHAIN)/bin/agondev-config
AGONDEV_MAKEFILE := $(shell "$(AGONDEV_CONFIG)" --makefile)
ifeq ($(strip $(AGONDEV_MAKEFILE)),)
$(error Cannot resolve AgonDev makefile using $(AGONDEV_CONFIG))
endif

RAM_START := 0x40000
RAM_SIZE := 0x70000
LDHAS_ARG_PROCESSING := 0
LDHAS_EXIT_HANDLER := 0
PYTHON := $(abspath ../../.venv/bin/python)

include $(AGONDEV_MAKEFILE)

# Pin the baseline dialect while retaining the toolchain's target flags.
CXXFLAGS += -std=c++14

.PHONY: check-sources
check-sources:
	@test -n "$(strip $(OBJS))" || { echo "No compilable test sources found in src/." >&2; exit 1; }

# Diagnose an empty source tree before invoking the linker.
$(LINKBINARY): | check-sources

.PHONY: sd-image headless
sd-image: all
	$(PYTHON) scripts/prepare_sd_image.py
headless:
	$(PYTHON) scripts/run_emulator.py
