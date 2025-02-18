#ifndef rangecod_h
#define rangecod_h

/*
  rangecod.h     headerfile for range encoding

  (c) Michael Schindler
  1997, 1998, 1999, 2000
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
  belived (NO WARRANTY!) to be patent-free here in Austria. Glen
  Langdon also confirmed my poinion that IBM UK did not protect that
  method.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston,
  MA 02111-1307, USA.

  Range encoding is based on an article by G.N.N. Martin, submitted
  March 1979 and presented on the Video & Data Recording Conference,
  Southampton, July 24-27, 1979. If anyone can name the original
  copyright holder of that article please contact me; this might
  allow me to make that article available on the net for general
  public.

  Range coding is closely related to arithmetic coding, except that
  it does renormalisation in larger units than bits and is thus
  faster. An earlier version of this code was distributed as byte
  oriented arithmetic coding, but then I had no knowledge of Martin's
  paper from 1979.

  The input and output is done by the INBYTE and OUTBYTE macros
  defined in the .c file; change them as needed; the first parameter
  passed to them is a pointer to the simz_rangecoder structure; extend that
  structure as needed (and don't forget to initialize the values in
  simz_start_encoding resp. simz_start_decoding). This distribution writes to
  stdout and reads from stdin.

  There are no global or static var's, so if the IO is thread save the
  whole simz_rangecoder is - unless GLOBALRANGECODER in rangecod.h is defined.

  For error recovery the last 3 bytes written contain the total number
  of bytes written since starting the encoder. This can be used to
  locate the beginning of a block if you have only the end.

  For some application using a global coder variable may provide a better
  performance. This will allow you to use only one coder at a time and
  will destroy thread savety. To enabble this feature uncomment the
  #define GLOBALRANGECODER line below.
*/
/* #define GLOBALRANGECODER */


#include "port.h"
#if 0    /* done in port.h */
#include <limits.h>
#if INT_MAX > 0xffff
typedef unsigned int uint4;
typedef unsigned short uint2;
#else
typedef unsigned long uint4;
typedef unsigned int uint2;
#endif
#endif

extern char coderversion[];

typedef uint4 simz_code_value;       /* Type of an rangecode value       */
                                /* must accomodate 32 bits          */
/* it is highly recommended that the total frequency count is less  */
/* than 1 << 19 to minimize rounding effects.                       */
/* the total frequency count MUST be less than 1<<23                */

typedef uint4 simz_freq; 

/* make the following private in the arithcoder object in C++	    */

typedef struct {
    uint4 low,           /* low end of interval */
          range,         /* length of interval */
          help;          /* bytes_to_follow resp. intermediate value */
    unsigned char buffer;/* buffer for input/output */
/* the following is used only when encoding */
    uint4 bytecount;     /* counter for outputed bytes  */
/* insert fields you need for input/output below this line! */
} simz_rangecoder;


/* supply the following as methods of the arithcoder object  */
/* omit the first parameter then (C++)                       */
#ifdef GLOBALRANGECODER
#define simz_start_encoding(rc,a,b) M_start_encoding(a,b)
#define simz_encode_freq(rc,a,b,c) M_encode_freq(a,b,c)
#define simz_encode_shift(rc,a,b,c) M_encode_shift(a,b,c)
#define simz_done_encoding(rc) M_done_encoding()
#define simz_start_decoding(rc) M_start_decoding()
#define simz_decode_culfreq(rc,a) M_decode_culfreq(a)
#define simz_decode_culshift(rc,a) M_decode_culshift(a)
#define simz_decode_update(rc,a,b,c) M_decode_update(a,b,c)
#define simz_decode_byte(rc) M_decode_byte()
#define simz_decode_short(rc) M_decode_short()
#define simz_done_decoding(rc) M_done_decoding()
#endif


/* Start the encoder                                         */
/* rc is the range coder to be used                          */
/* c is written as first byte in the datastream (header,...) */
void simz_start_encoding( simz_rangecoder *rc, char c, int initlength);


/* Encode a symbol using frequencies                         */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
/* or (a lot faster): tot_f = 1<<shift                       */
void simz_encode_freq( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq tot_f );
void simz_encode_shift( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq shift );

/* Encode a byte/short without modelling                     */
/* rc is the range coder to be used                          */
/* b,s is the data to be encoded                             */
#define encode_byte(ac,b)  simz_encode_shift(ac,(simz_freq)1,(simz_freq)(b),(simz_freq)8)
#define encode_short(ac,s) simz_encode_shift(ac,(simz_freq)1,(simz_freq)(s),(simz_freq)16)


/* Finish encoding                                           */
/* rc is the range coder to be shut down                     */
/* returns number of bytes written                           */
uint4 simz_done_encoding( simz_rangecoder *rc );



/* Start the decoder                                         */
/* rc is the range coder to be used                          */
/* returns the char from simz_start_encoding or EOF               */
int simz_start_decoding( simz_rangecoder *rc );

/* Calculate culmulative frequency for next symbol. Does NO update!*/
/* rc is the range coder to be used                          */
/* tot_f is the total frequency                              */
/* or: totf is 1<<shift                                      */
/* returns the <= culmulative frequency                      */
simz_freq simz_decode_culfreq( simz_rangecoder *rc, simz_freq tot_f );
simz_freq simz_decode_culshift( simz_rangecoder *ac, simz_freq shift );

/* Update decoding state                                     */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
void simz_decode_update( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq tot_f);
#define decode_update_shift(rc,f1,f2,f3) simz_decode_update((rc),(f1),(f2),(simz_freq)1<<(f3));

/* Decode a byte/short without modelling                     */
/* rc is the range coder to be used                          */
unsigned char simz_decode_byte(simz_rangecoder *rc);
unsigned short simz_decode_short(simz_rangecoder *rc);


/* Finish decoding                                           */
/* rc is the range coder to be used                          */
void simz_done_decoding( simz_rangecoder *rc );

#endif
