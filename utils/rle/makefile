# Detect operating system
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Linux)
    CC = gcc
    CFLAGS = -std=c99 -O2 -Wall
endif

ifeq ($(UNAME_S),Darwin)
    CC = clang
    CFLAGS = -std=c99 -O2 -Wall
endif

# Source files and targets
SRCS = rlecompress.c rledecompress.c
TARGETS = rlecompress rledecompress

all: $(TARGETS)

rlecompress: rlecompress.c
	$(CC) $(CFLAGS) -o rlecompress rlecompress.c

rledecompress: rledecompress.c
	$(CC) $(CFLAGS) -o rledecompress rledecompress.c

clean:
	rm -f $(TARGETS)
