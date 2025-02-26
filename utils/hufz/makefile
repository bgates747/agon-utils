# Detect OS
UNAME_S := $(shell uname -s)

# Compiler selection
ifeq ($(UNAME_S),Linux)
    CC = gcc
    CFLAGS = -std=c11 -O2 -Wall -Wextra
endif

ifeq ($(UNAME_S),Darwin)
    CC = clang
    CFLAGS = -std=c11 -O2 -Wall -Wextra
endif

# Targets
TARGET = hufz
SRC = hufz.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)
