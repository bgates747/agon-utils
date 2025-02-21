# Makefile for mskz
CC      = gcc
CFLAGS  = -Wall -Wextra -O2
TARGET  = mskz
SOURCES = mskz.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES)

clean:
	rm -f $(TARGET)
