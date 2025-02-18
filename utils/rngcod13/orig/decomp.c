/*
  decomp.c     headerfile for quasistatic probability model

  (c) Michael Schindler
  1997, 1998, 2000
  http://www.compressconsult.com/
  michael@compressconsult.com

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.  It may be that this
  program violates local patents in your country, however it is
  belived (NO WARRANTY!) to be patent-free here in Austria.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston,
  MA 02111-1307, USA.

  decomp is an example decompressor able to decompress the files
  produced by comp.c

  Note that I do not think that an order 0 model as here is good;
  For better compression see for example my freeware szip.
  http://www.compressconsult.com/szip/
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
{   fprintf(stderr,"decomp [inputfile [outputfile]]\n");
    fprintf(stderr,"decomp (c)1997.1998 Michael Schindler, michael@compressconsult.com\n"); 
    exit(1);
}

int main( int argc, char *argv[] )
{   int ch, syfreq, ltfreq;
    rangecoder rc;
    qsmodel qsm;
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

    /* init the model the same as in the compressor */
    initqsmodel(&qsm,257,12,2000,NULL,0);
    start_decoding(&rc);

    while (1)
    {
        ltfreq = decode_culshift(&rc,12);
        ch = qsgetsym(&qsm, ltfreq);
        if (ch==256)  /* check for end-of-file */
            break;
        putc(ch,stdout);
        qsgetfreq(&qsm,ch,&syfreq,&ltfreq);
        decode_update( &rc, syfreq, ltfreq, 1<<12);
        qsupdate(&qsm,ch);
    }
    qsgetfreq(&qsm,256,&syfreq,&ltfreq);
    decode_update( &rc, syfreq, ltfreq, 1<<12);
    done_decoding(&rc);
    deleteqsmodel(&qsm);

    return 0;
}
