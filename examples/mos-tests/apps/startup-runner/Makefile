NAME := startup-runner
AGONDEV_TOOLCHAIN ?= /home/smith/Agon/agondev/release
LDHAS_ARG_PROCESSING := 1
LDHAS_EXIT_HANDLER := 0
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CXXFLAGS += -std=c++14 -I../runner/include
obj/main.o: include/generated.h include/sha256.h include/script.h include/continuation.h ../runner/include/recording.h ../runner/include/recorded_lifecycle.h ../runner/include/mos_storage.h
obj/probe.o: ../runner/src/capture.asm ../runner/src/storage.asm
