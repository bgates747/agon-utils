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

SRCS = tvc.c
TARGET = tvc

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS)

clean:
	rm -f $(TARGET)
