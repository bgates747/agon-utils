/*
  comp1.c     demo program for order 1 range coder using 256 qsmodels

  (c) Michael Schindler
  1999
  http://www.compressconsult.com/
  michael@compressconsult.com

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston,
  MA 02111-1307, USA.

  comp1 is an example compressor trying to compress files with a simple
  order 1 model. The files can be decompressed by decomp1.

  Note that I do not think that an order 1 model as here is good;
  For better compression see for example my freeware szip.
  http://www.compressconsult.com/szip/
  or ask me as consultant what compression method fits your data best.
*/

#include <stdio.h>
#include <stdlib.h>
#ifndef unix
#include <io.h>
#include <fcntl.h>
#endif
#include <string.h>
#include <ctype.h>
#include "port.h"
#include "qsmodel.h"
#include "rangecod.h"

void usage()
{   fprintf(stderr,"comp1 [inputfile [outputfile]]\n");
    fprintf(stderr,"comp1 (c)1999 Michael Schindler, michael@compressconsult.com\n"); 
    exit(1);
}

int main( int argc, char *argv[] )
{   int ch, syfreq, ltfreq, lastchar=0;
    rangecoder rc;
    qsmodel qsm[256];

    if ((argc > 3) || ((argc>0) && (argv[1][0]=='-')))
        usage();

    if ( argc<1 )
        fprintf( stderr, "stdin" );
    else
    {   freopen( argv[1], "rb", stdin );
        fprintf( stderr, "%s", argv[1] );
    }
    if ( argc<2 )
        fprintf( stderr, " to stdout\n" );
    else
    {   freopen( argv[2], "wb", stdout );
        fprintf( stderr, " to %s\n", argv[2] );
    }
    fprintf( stderr, "%s\n", coderversion);

#ifndef unix
    setmode( fileno( stdin ), O_BINARY );
    setmode( fileno( stdout ), O_BINARY );
#endif

    /* make an alphabet with 257 symbols, use 256 as end-of-file */
    for (ch=0; ch<256; ch++)
        initqsmodel(qsm+ch,257,12,2000,NULL,1);
    start_encoding(&rc,0,0);

    /* do the coding */
    while ((ch=getc(stdin))!=EOF)
    {   qsgetfreq(qsm+lastchar,ch,&syfreq,&ltfreq);
        encode_shift(&rc,syfreq,ltfreq,12);
        qsupdate(qsm+lastchar,ch);
        lastchar = ch;
    }
    /* write 256 as end-of-file */
    qsgetfreq(qsm+lastchar,256,&syfreq,&ltfreq);
    encode_shift(&rc,syfreq,ltfreq,12);

    done_encoding(&rc);
    for (ch=0; ch<256; ch++)
        deleteqsmodel(qsm+ch);

    return 0;
}
