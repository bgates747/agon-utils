CC = gcc
CFLAGS = -O2 -Wall -fomit-frame-pointer -funroll-loops
TARGET = szip

SRC = szip.c rangecod.c qsmodel.c bitmodel.c sz_mod4.c sz_srt.c reorder.c
OBJ = $(SRC:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

clean:
	rm -f $(OBJ) $(TARGET)
