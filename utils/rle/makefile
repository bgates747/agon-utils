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

# Source files and target
SRCS = rle2.c
TARGET = rle2

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS)

clean:
	rm -f $(TARGET)
