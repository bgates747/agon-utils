NAME := capture-controls
AGONDEV_TOOLCHAIN ?= /home/smith/Agon/agondev/release
LDHAS_ARG_PROCESSING := 0
LDHAS_EXIT_HANDLER := 0
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CXXFLAGS += -std=c++14
obj/probe.o: ../runner/src/capture.asm
