/*
  dummycod.c     range encoding

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

  dummycod.c is a dummy version of the rangecod.c
*/
#include "port.h"
#include "rangecod.h"
#include <stdio.h>

#ifdef GLOBALRANGECODER
static rangecoder rngc;
char coderversion[]="dummycoder 1.0 GLOBALRANGECODER (c) 1997, 1998 Michael Schindler";
#define RNGC (rngc)
#define M_outbyte(a) outbyte(&rngc,a)
#define M_inbyte inbyte(&rngc)
#define enc_normalize(rc) M_enc_normalize()
#define dec_normalize(rc) M_dec_normalize()
#else
char coderversion[]="dummycoder 1.0 (c) 1997, 1998 Michael Schindler";
#define RNGC (*rc)
#define M_outbyte(a) outbyte(rc,a)
#define M_inbyte inbyte(rc)
#endif


/* all IO is done by these macros - change them if you want to */
/* no checking is done - do it here if you want it             */
/* cod is a pointer to the used rangecoder                     */
#define outbyte(cod,x) putc(x,stdout)
#define inbyte(cod)    getc(stdin)


/* rc is the range coder to be used                            */
/* c is written as first byte in the datastream                */
/* one could do without c, but then you have an additional if  */
/* per outputbyte.                                             */
void start_encoding( rangecoder *rc, char c, int initlength )
{   M_outbyte(c);
}

/* Encode a symbol using frequencies                         */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
/* or (faster): tot_f = 1<<shift                             */
void encode_freq( rangecoder *rc, freq sy_f, freq lt_f, freq tot_f )
{   if ((tot_f & 0x8000 == 0x8000) && (sy_f + lt_f > tot_f))
        fprintf(stderr, "dummycoder: lt_f + sy_f > tot_f");
    M_outbyte((char)(sy_f>>8));
    M_outbyte((char)(sy_f & 0xff));
    M_outbyte((char)(lt_f>>8));
    M_outbyte((char)(lt_f & 0xff));
    M_outbyte((char)(tot_f>>8));
    M_outbyte((char)(tot_f & 0xff));
}


void encode_shift( rangecoder *rc, freq sy_f, freq lt_f, freq shift )
{   if (sy_f + lt_f > (freq)1<<shift)
        fprintf(stderr, "dummycoder_shift: lt_f + sy_f > tot_f");
    encode_freq(rc,sy_f,lt_f,shift|0x8000);
}


/* Finish encoding                                           */
/* rc is the range coder to be used                          */
/* actually not that many bytes need to be output, but who   */
/* cares. I output them because decode will read them :)     */
/* the return value is the number of bytes written           */
uint4 done_encoding( rangecoder *rc )
{   return 0;
}


/* Start the decoder                                         */
/* rc is the range coder to be used                          */
/* returns the char from start_encoding or EOF               */
int start_decoding( rangecoder *rc )
{   return M_inbyte;
}


/* Calculate culmulative frequency for next symbol. Does NO update!*/
/* rc is the range coder to be used                          */
/* tot_f is the total frequency                              */
/* or: totf is 1<<shift                                      */
/* returns the culmulative frequency                         */
freq decode_culfreq( rangecoder *rc, freq tot_f )
{   RNGC.help = (uint)(M_inbyte)<<8;  /* sy_f in help */
    RNGC.help |= M_inbyte;
    RNGC.range = (uint)(M_inbyte)<<8; /* lt_f in range */
    RNGC.range |= M_inbyte;
    RNGC.low = (uint)(M_inbyte)<<8;   /* tot_f in low */
    RNGC.low |= M_inbyte;
    if (tot_f != RNGC.low)
        fprintf(stderr, "decode_cul* wrong total; got %4d expected %4d\n",
            tot_f, RNGC.low);
    return (RNGC.help>>1) + RNGC.range;
}


freq decode_culshift( rangecoder *rc, freq shift )
{   uint tmp=decode_culfreq(rc,shift|0x8000);
    RNGC.low = 1 << (RNGC.low & 0x7fff);
    return tmp;
}


/* Update decoding state                                     */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
void decode_update( rangecoder *rc, freq sy_f, freq lt_f, freq tot_f)
{   if (sy_f != RNGC.help)
        fprintf(stderr, "decode_update wrong sy_f; got %4d expected %4d\n",
            sy_f, RNGC.help);
    if (lt_f != RNGC.range)
        fprintf(stderr, "decode_update wrong lt_f; got %4d expected %4d\n",
            lt_f, RNGC.range);
    if (tot_f != RNGC.low)
        fprintf(stderr, "decode_update wrong total; got %4d expected %4d\n",
            tot_f, RNGC.low);
}


/* Decode a byte/short without modelling                     */
/* rc is the range coder to be used                          */
unsigned char decode_byte(rangecoder *rc)
{   return decode_culshift(rc,8);
}

unsigned short decode_short(rangecoder *rc)
{   return decode_culshift(rc,16);
}


/* Finish decoding                                           */
/* rc is the range coder to be used                          */
void done_decoding( rangecoder *rc )
{}
