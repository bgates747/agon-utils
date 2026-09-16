NAME := w04-assembly
AGONDEV_TOOLCHAIN := /home/smith/Agon/agondev/release
LDHAS_ARG_PROCESSING := 0
LDHAS_EXIT_HANDLER := 0
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CXXFLAGS += -std=c++14
.PHONY: listings
listings: all
	$(TOOLBINDIR)/ez80-none-elf-objdump -dr obj/main.o > bin/main-disassembly.txt
