NAME := mos-runner
AGONDEV_TOOLCHAIN ?= /home/smith/Agon/agondev/release
LDHAS_ARG_PROCESSING := 0
LDHAS_EXIT_HANDLER := 0
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CXXFLAGS += -std=c++14
obj/main.o: include/catalogue_generated.h include/lifecycle.h
