CFLAGS = -O3 -Wall -fomit-frame-pointer -funroll-loops

ext = .exe

all: qsmodel.o rangecod.o comp.o decomp.o comp$(EXT) decomp$(EXT) comp1$(EXT) decomp1$(EXT) simple_c$(EXT) simple_d$(EXT)
compare: rangec95.o comp95$(EXT) decomp95$(EXT)

qsmodel.o: port.h qsmodel.h qsmodel.c
rangecod.o: port.h rangecod.h rangecod.c
comp.o: port.h qsmodel.h rangecod.h comp.c
decomp.o: port.h qsmodel.h rangecod.h decomp.c
comp1.o: port.h qsmodel.h rangecod.h comp1.c
decomp1.o: port.h qsmodel.h rangecod.h decomp1.c
simple_c.o: port.h rangecod.h simple_c.c
simple_d.o: port.h rangecod.h simple_d.c
rangec95.o: port.h rangecod.h rangecod.c renorm95.c
	$(CC) $(CFLAGS) -c rangecod.c -DRENORM95 -o rangec95.o

comp$(EXT): qsmodel.o rangecod.o comp.o
decomp$(EXT): qsmodel.o rangecod.o decomp.o
comp1$(EXT): qsmodel.o rangecod.o comp1.o
decomp1$(EXT): qsmodel.o rangecod.o decomp1.o
simple_c$(EXT): rangecod.o simple_c.o
simple_d$(EXT): rangecod.o simple_d.o
comp95$(EXT): qsmodel.o rangec95.o comp.o
	$(CC) $(LNFLAGS) $^ -o $@$(EXT)
decomp95$(EXT): qsmodel.o rangec95.o decomp.o
	$(CC) $(LNFLAGS) $^ -o $@$(EXT)
