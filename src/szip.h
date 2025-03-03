
#if !defined port_h
#define port_h

typedef unsigned int uint;

#if defined GCC
#define Inline inline
#else
#define Inline __inline
#endif

/* change to 1 if types.h exists */
#if 1
#include <sys/types.h>
#define uint2 u_int16_t
#define uint4 u_int32_t
/* uint is alredy defined in types.h */

#else
#include <limits.h>
#if INT_MAX > 0x7FFF
typedef unsigned short uint2;  /* two-byte integer (large arrays)      */
typedef unsigned int   uint4;  /* four-byte integers (range needed)    */
#else
typedef unsigned int   uint2;
typedef unsigned long  uint4;
#endif /* INT_MAX */

typedef unsigned int uint;     /* fast unsigned integer, 2 or 4 bytes  */

#endif


#endif

#ifndef BITMODEL_H
#define BITMODEL_H

/*
  bitmodel.h     headerfile for bit indexed trees probability model

  (c) Michael Schindler
  1997, 1998
  http://www.compressconsult.com or http://eiunix.tuwien.ac.at/~michael
  michael@compressconsult.com        michael@eiunix.tuwien.ac.at

  based on: Peter Fenwick: A New Data Structure for Cumulative Probability Tables
  Technical Report 88, Dep. of Computer Science, University of Auckland, NZ

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.  It may be that this
  program violates local patents in your country, however it is
  belived (NO WARRANTY!) to be patent-free here in Austria and I am
  not aware of a violation elsewhere.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston,
  MA 02111-1307, USA.

  Bitmodel implements bit indexed trees for frequency storage described
  by Peter Fenwick: A New Data Structure for Cumulative Probability Tables
  Technical Report 88, Dep. of Computer Science, University of Auckland, NZ.
  It features a fast method for cumulative frequency storage and updating.
  The difference to the fenwick paper is the way the table is recalculated
  after rescaling; the method here is faster.

  There is a compiletime switch; if EXCLUDEONUPDATE is defined symbols
  are excluded on update; to be able to use them again you have to call
  the include function for that symbol.

  The module provides functions for creation, reset, deletion, query for
  probabilities, queries for symbols, reenabling symbols and model updating.
*/

// #include "port.h"

#define EXCLUDEONUPDATE

typedef struct {
    int n,             /* number of symbols */
        totalfreq,     /* total frequency count (without excluded symbols) */
        max_totf,      /* maximum allowed total frequency count */
        incr,          /* increment per update */
        mask;          /* initial bitmask used for search */
    uint2 *f,          /* frequency for the symbol; first bit set if excluded */
        *cf;           /* array of cumulative frequencies */
} bitmodel;

/* initialisation of bitmodel                          */
/* m   bitmodel to be initialized                      */
/* n   number of symbols in that model                 */
/* max_totf  maximum allowed total frequency count     */
/* rescale  desired rescaling interval, must be <max_totf/2 */
/* init  array of int's to be used for initialisation (NULL ok) */
void initbitmodel( bitmodel *m, int n, int max_totf, int rescale,
   int *init );

/* reinitialisation of bitmodel                        */
/* m   bitmodel to be initialized                      */
/* init  array of int's to be used for initialisation (NULL ok) */
void resetbitmodel( bitmodel *m, int *init);


/* deletion of bitmodel m                              */
void deletebitmodel( bitmodel *m );


/* retrieval of estimated frequencies for a symbol     */
/* m   bitmodel to be questioned                       */
/* sym  symbol for which data is desired; must be <n   */
/* sy_f frequency of that symbol                       */
/* lt_f frequency of all smaller symbols together      */
/* the total frequency can be obtained with bit_totf   */
void bitgetfreq( bitmodel *m, int sym, int *sy_f, int *lt_f);

/* find out total frequency for a bitmodel             */
/* m   bitmodel to be questioned                       */
#define bittotf(m) ((m)->totalfreq)

/* scales the culmulative frequency tables by 0.5 and keeps nonzero values */
void scalefreqbitmod(bitmodel *m);

/* find out symbol for a given cumulative frequency    */
/* m   bitmodel to be questioned                       */
/* lt_f  cumulative frequency                          */
int bitgetsym( bitmodel *m, int lt_f );


/* update model                                        */
/* m   bitmodel to be updated                          */
/* sym  symbol that occurred (must be <n from init)    */
void bitupdate( bitmodel *m, int sym );


#ifdef EXCLUDEONUPDATE
/* update model and exclude symbol                     */
/* m   bitmodel to be updated                          */
/* sym  symbol that occurred (must be <n from init)    */
void bitupdate_ex( bitmodel *m, int sym );


/* deactivate symbol                                   */
/* m   bitmodel to be updated                          */
/* sym  symbol to be deactivated                       */
void bitdeactivate( bitmodel *m, int sym );

/* reactivate symbol                                   */
/* m   bitmodel to be updated                          */
/* sym  symbol to be reactivated                       */
void bitreactivate( bitmodel *m, int sym );
#endif

#endif

#ifndef QSMODEL_H
#define QSMODEL_H

/*
  qsmodel.h     headerfile for quasistatic probability model

  (c) Michael Schindler
  1997, 1998
  http://www.compressconsult.com/ or http://eiunix.tuwien.ac.at/~michael
  michael@compressconsult.com        michael@eiunix.tuwien.ac.at

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

  Qsmodel is a quasistatic probability model that periodically
  (at chooseable intervals) updates probabilities of symbols;
  it also allows to initialize probabilities. Updating is done more
  frequent in the beginning, so it adapts very fast even without
  initialisation.

  it provides function for creation, deletion, query for probabilities
  and symbols and model updating.

  for usage see example.c
*/

// #include "port.h"

typedef struct {
    int n,             /* number of symbols */
        left,          /* symbols to next rescale */
        nextleft,      /* symbols with other increment */
        rescale,       /* intervals between rescales */
        targetrescale, /* should be interval between rescales */
        incr,          /* increment per update */
        searchshift;   /* shift for lt_freq before using as index */
    uint2 *cf,         /* array of cumulative frequencies */
        *newf,         /* array for collecting ststistics */
        *search;       /* structure for searching on decompression */
} qsmodel;

/* initialisation of qsmodel                           */
/* m   qsmodel to be initialized                       */
/* n   number of symbols in that model                 */
/* lg_totf  base2 log of total frequency count         */
/* rescale  desired rescaling interval, should be < 1<<(lg_totf+1) */
/* init  array of int's to be used for initialisation (NULL ok) */
/* compress  set to 1 on compression, 0 on decompression */
void initqsmodel( qsmodel *m, int n, int lg_totf, int rescale,
   int *init, int compress );

/* reinitialisation of qsmodel                         */
/* m   qsmodel to be initialized                       */
/* init  array of int's to be used for initialisation (NULL ok) */
void resetqsmodel( qsmodel *m, int *init);


/* deletion of qsmodel m                               */
void deleteqsmodel( qsmodel *m );


/* retrieval of estimated frequencies for a symbol     */
/* m   qsmodel to be questioned                        */
/* sym  symbol for which data is desired; must be <n   */
/* sy_f frequency of that symbol                       */
/* lt_f frequency of all smaller symbols together      */
/* the total frequency is 1<<lg_totf                   */
void qsgetfreq( qsmodel *m, int sym, int *sy_f, int *lt_f );


/* find out symbol for a given cumulative frequency    */
/* m   qsmodel to be questioned                        */
/* lt_f  cumulative frequency                          */
int qsgetsym( qsmodel *m, int lt_f );


/* update model                                        */
/* m   qsmodel to be updated                           */
/* sym  symbol that occurred (must be <n from init)    */
void qsupdate( qsmodel *m, int sym );

#endif

#ifndef rangecod_h
#define rangecod_h

/*
  rangecod.h     headerfile for range encoding

  (c) Michael Schindler
  1997, 1998, 1999
  http://www.compressconsult.com/ or http://eiunix.tuwien.ac.at/~michael
  michael@compressconsult.com        michael@eiunix.tuwien.ac.at

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
  copyright holder of that article or locate G.N.N. Martin please
  contact me; this might allow me to make that article available on
  the net for general public.

  Range coding is closely related to arithmetic coding, except that
  it does renormalisation in larger units than bits and is thus
  faster. An earlier version of this code was distributed as byte
  oriented arithmetic coding, but then I had no knowledge of Martin's
  paper from seventy-nine.

  The input and output is done by the INBYTE and OUTBYTE macros
  defined in the .c file; change them as needed; the first parameter
  passed to them is a pointer to the rangecoder structure; extend that
  structure as needed (and don't forget to initialize the values in
  start_encoding resp. start_decoding). This distribution writes to
  stdout and reads from stdin.

  There are no global or static var's, so if the IO is thread save the
  whole rangecoder is - unless GLOBALRANGECODER is defined.

  For error recovery the last 3 bytes written contain the total number
  of bytes written since starting the encoder. This can be used to
  locate the beginning of a block if you have only the end.

  For some application using a global coder variable may provide a better
  performance. This will allow you to use only one coder at a time and
  will destroy thread savety. To enabble this feature uncomment the
  #define GLOBALRANGECODER line below.
*/
#define GLOBALRANGECODER


// #include "port.h"
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

typedef uint4 code_value;       /* Type of an rangecode value       */
                                /* must accomodate 32 bits          */
/* it is highly recommended that the total frequency count is less  */
/* than 1 << 19 to minimize rounding effects.                       */
/* the total frequency count MUST be less than 1<<23                */

typedef uint4 freq; 

/* make the following private in the arithcoder object in C++	    */

typedef struct {
    uint4 low,           /* low end of interval */
          range,         /* length of interval */
          help;          /* bytes_to_follow resp. intermediate value */
    unsigned char buffer;/* buffer for input/output */
/* the following is used only when encoding */
    uint4 bytecount;     /* counter for outputed bytes  */
/* insert fields you need for input/output below this line! */
} rangecoder;


/* supply the following as methods of the arithcoder object  */
/* omit the first parameter then (C++)                       */
#ifdef GLOBALRANGECODER
#define start_encoding(rc,a,b) M_start_encoding(a,b)
#define encode_freq(rc,a,b,c) M_encode_freq(a,b,c)
#define encode_shift(rc,a,b,c) M_encode_shift(a,b,c)
#define done_encoding(rc) M_done_encoding()
#define start_decoding(rc) M_start_decoding()
#define decode_culfreq(rc,a) M_decode_culfreq(a)
#define decode_culshift(rc,a) M_decode_culshift(a)
#define decode_update(rc,a,b,c) M_decode_update(a,b,c)
#define decode_byte(rc) M_decode_byte()
#define decode_short(rc) M_decode_short()
#define done_decoding(rc) M_done_decoding()
#endif


/* Start the encoder                                         */
/* rc is the range coder to be used                          */
/* c is written as first byte in the datastream (header,...) */
void start_encoding( rangecoder *rc, char c, int initlength);


/* Encode a symbol using frequencies                         */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
/* or (a lot faster): tot_f = 1<<shift                       */
void encode_freq( rangecoder *rc, freq sy_f, freq lt_f, freq tot_f );
void encode_shift( rangecoder *rc, freq sy_f, freq lt_f, freq shift );

/* Encode a byte/short without modelling                     */
/* rc is the range coder to be used                          */
/* b,s is the data to be encoded                             */
#define encode_byte(ac,b)  encode_shift(ac,(freq)1,(freq)(b),(freq)8)
#define encode_short(ac,s) encode_shift(ac,(freq)1,(freq)(s),(freq)16)


/* Finish encoding                                           */
/* rc is the range coder to be shut down                     */
/* returns number of bytes written                           */
uint4 done_encoding( rangecoder *rc );



/* Start the decoder                                         */
/* rc is the range coder to be used                          */
/* returns the char from start_encoding or EOF               */
int start_decoding( rangecoder *rc );

/* Calculate culmulative frequency for next symbol. Does NO update!*/
/* rc is the range coder to be used                          */
/* tot_f is the total frequency                              */
/* or: totf is 1<<shift                                      */
/* returns the <= culmulative frequency                      */
freq decode_culfreq( rangecoder *rc, freq tot_f );
freq decode_culshift( rangecoder *ac, freq shift );

/* Update decoding state                                     */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
void decode_update( rangecoder *rc, freq sy_f, freq lt_f, freq tot_f);
#define decode_update_shift(rc,f1,f2,f3) decode_update((rc),(f1),(f2),(freq)1<<(f3));

/* Decode a byte/short without modelling                     */
/* rc is the range coder to be used                          */
unsigned char decode_byte(rangecoder *rc);
unsigned short decode_short(rangecoder *rc);


/* Finish decoding                                           */
/* rc is the range coder to be used                          */
void done_decoding( rangecoder *rc );

#endif

#ifndef REORDER_H

// #include "port.h"

void reorder(unsigned char *in, unsigned char *out, uint4 length, uint recordsize);

void unreorder(unsigned char *in, unsigned char *out, uint4 length, uint recordsize);

#endif // REORDER_H

/* b_i_t.h                                                                   */
/* this implements bit indexed trees for culmulative frequency storeage      */
/* described in                                                              */
/* Peter Fenwick: A New Data Structure for Cumulative Probability Tables     */
/* Technical Report 88, Dep. of Computer Science, University of Auckland, NZ */

#ifndef b_i_t_h
#define b_i_t_h

// #include "port.h"
// #include "rangecod.h"
//typedef uint4 freq;
typedef uint4 symb;

typedef struct {
   symb size, mask;
   freq *cf, *f, totfreq;
} cumtbl;

/* returns the culmulative frequency < the given symbol */
Inline freq getcf(symb s, cumtbl *tbl);

/* updates the given frequency */
#define updatefreq(_s,_tbl,_delta)      \
 { int upd_delta = (_delta);            \
   symb upd_s = (_s);                   \
   (_tbl)->f[upd_s] += upd_delta;       \
   updatecumonly(upd_s,_tbl,upd_delta); }

/* updates the given culmulative frequency */
Inline void updatecumonly(symb s, cumtbl *tbl, int delta);

/* get symbol for this culmulative frequency */
Inline symb getsym(freq f, cumtbl *tbl);

/* scales the culmulative frequency tables by 0.5 and keeps nonzero values */
void scalefreq(cumtbl *tbl);

/* scales the culmulative frequency tables by 0.5 and keeps nonzero values */
void scalefreqcond(cumtbl *tbl, uint *donotuse);

/* allocates memory for the frequency table and initializes it */
int initfreq(cumtbl *tbl, symb tblsize, freq initvalue);

/* does the obvious thing */
void freefreq(cumtbl *tbl);

#endif

// SZ error messages
#ifndef ERR_H
#define ERR_H

extern int data_error(int errnum);

//#ifdef DEBUG                // give last 8 bits too 
//#define sz_error(x) data_error(x)
//#else
//#define sz_error(x) data_error((x)&~0xff)
//#endif
#define sz_error(x) do{fprintf(stderr,"Error #%x\n",x); abort();}while(0)

// those are ok:
#define NOMEM			0x6500
#define SZ_NOMEM_HASH		0x6502
#define SZ_NOMEM_SORT		0x6503

// those are a bug:
#define UNEXPECTED		0x6600
#define SZ_NOTCYCLIC		0x6601
#define SZ_NOTFOUND			0x6602
#define SZ_NOTIMPLEMENTED	0x6603
#define SZ_DOUBLEINDIRECT   0x6604
#define AR_OUTSTANDING		0x6605

#endif

#ifndef SZIP_DEBUG_H
#define SZIP_DEBUG_H

#include <stdarg.h>
#include <stdio.h>
// #include "port.h"

// Debug flag: Set to 1 to enable debug output, 0 to disable
#ifndef SZ_DEBUG
#define SZ_DEBUG 1
#endif

// Debug log function
static inline void szip_debug_log(const char *format, ...) {
    #if SZ_DEBUG == 1
    va_list ap;
    va_start(ap, format);
    flockfile(stderr);   // Thread-safe
    vfprintf(stderr, format, ap);
    fflush(stderr);
    funlockfile(stderr);
    va_end(ap);
    #endif
}

// Hex dump function
static inline void hex_dump(const unsigned char *buf, uint4 len) {
    #if SZ_DEBUG == 1
    uint4 i;
    flockfile(stderr);
    for (i = 0; i < len; i++) {
        fprintf(stderr, "%02X ", buf[i]);
        if ((i + 1) % 16 == 0) fprintf(stderr, "\n");
    }
    if (len % 16 != 0) fprintf(stderr, "\n");
    fflush(stderr);
    funlockfile(stderr);
    #endif
}

#endif  // SZIP_DEBUG_H

#ifndef SZIP_H

// #define GLOBALRANGECODER
// #define MODELGLOBAL

// #include "rangecod.h"
// #include "qsmodel.h"
// #include "bitmodel.h"
// #include "sz_mod4.h"
// #include "sz_srt.h"
// #include "reorder.h"

#endif // SZIP_H

/* sz_model4.h (c) Michael Schindler 1998 */
#ifndef SZ_MODEL4_H
#define SZ_MODEL4_H

// #include "port.h"
// #include "qsmodel.h"
// #include "bitmodel.h"
// #include "rangecod.h"

#define ALPHABETSIZE 256
#define CACHESIZE 32
#define MTFSIZE 20
#define MTFHISTSIZE 256  /* must pe power of 2 */
// #define MODELGLOBAL

typedef struct {
    uint sym, next;
} mtfentry;

typedef struct cacheS *cacheptr;

typedef struct cacheS {
    unsigned char symbol, sy_f, weight, what;
    cacheptr next, prev;
} cacheentry;

typedef struct {
    uint whatmod[3];  /* probabilities for the submodels */
    cacheptr newest,  /* points to newest element in cache */
             lastnew; /* points to last element with heigher weight */
    uint cachetotf;   /* total frequency count in cache */
    uint mtffirst;    /* where to find the newest entry in mtfhist */
    uint mtfsize;     /* size of mtflist */
    uint mtfsizeact;  /* size of active mtflist */
    cacheptr lastseen[ALPHABETSIZE]; /* tell if and where symbol is in cache */
    cacheentry cache[CACHESIZE]; /* cache */
    mtfentry mtfhist[MTFHISTSIZE];
    bitmodel full;    /* fallback model */
    qsmodel mtfmod;   /* probabilities for mtf ranks */
    qsmodel rlemod[5];
    rangecoder ac;
    uint compress;    /* 1 on compression, 0 on decompression */
} sz_model;

#ifdef MODELGLOBAL
#define initmodel(m,a,b) M_initmodel(a,b)
#define fixafterfirst(m) M_fixafterfirst()
#define deletemodel(m) M_deletemodel()
#define sz_finishrun(m) M_sz_finishrun()
#define sz_encode(m,a,b) M_sz_encode(a,b)
#define sz_decode(m,a,b) M_sz_decode(a,b)
#endif


/* initialisation if the model */
/* headersize -1 means decompression */
/* first is the first byte written by the arithcoder */
void initmodel(sz_model *m, int headersize, unsigned char *first);

/* call fixafterfirst after encoding/decoding the first run */
void fixafterfirst(sz_model *m);

/* deletion of the model */
void deletemodel(sz_model *m);

/* encode/decode a run of equal symbols */
void sz_encode(sz_model *m, uint symbol, uint4 runlength);
void sz_decode(sz_model *m, uint *symbol, uint4 *runlength);


#endif

#ifndef SZ_SRT_H
#define SZ_SRT_H
// #include "port.h"


// inout: bytes to be sorted; sorted bytes on return. must be length+order bytes long
// length: number of bytes in inout
// *indexlast: returns position of last context (needed for unsort)
// order: order of context used in sorting (must be >=3)
// the code assumes length>=order
// and inout is length+order bytes long (only the first length need to be filled)
void sz_srt(unsigned char *inout, uint4 length, uint4 *indexlast, unsigned int order);


// in: bytes to be unsorted
// out: unsorted bytes; if NULL output is written to stdout
// length: number of bytes in in (and out)
// indexlast: position of last context (as returned bt sorttrans)
// counts: number of occurances of each byte in in (if NULL it will be calculated)
// order: order of context used in sorting (must be >=3)
// the code assumes length>=order
void sz_unsrt(unsigned char *in, unsigned char *out, uint4 length, uint4 indexlast,
			   uint4 *counts, unsigned int order);


// comment the following #defines if you dont want them
#define SZ_SRT_O4
//#define SZ_UNSRT_O4
#define SZ_SRT_BW

// alternate sorter for order 4 (different method, same result)
#if defined SZ_SRT_O4
void sz_srt_o4(unsigned char *inout, uint4 length, uint4 *indexlast);
#endif


// alternate unsorter for order 4 (different method (hash), same result)
#if defined SZ_UNSRT_O4
void sz_unsrt_o4(unsigned char *in, unsigned char *out, uint4 length, uint4 indexlast,
				 uint4 *counts);
#endif


#if defined SZ_SRT_BW
// unlimited context sort (BWT but with context before symbol)
void sz_srt_BW(unsigned char *inout, uint4 length, uint4 *indexfirst);

// unsorter for unlimited context sort
void sz_unsrt_BW(unsigned char *in, unsigned char *out, uint4 length,
			   uint4 indexfirst, uint4 *counts);
#endif
#endif
