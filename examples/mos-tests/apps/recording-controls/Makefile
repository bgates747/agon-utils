NAME := recording-controls
AGONDEV_TOOLCHAIN ?= /home/smith/Agon/agondev/release
LDHAS_ARG_PROCESSING := 0
LDHAS_EXIT_HANDLER := 0
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CXXFLAGS += -std=c++14 -I../runner/include
obj/main.o: ../runner/include/recording.h ../runner/include/mos_storage.h ../runner/include/recorded_lifecycle.h
obj/probe.o: ../runner/src/capture.asm ../runner/src/storage.asm
