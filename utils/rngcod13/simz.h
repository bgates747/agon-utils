
/*********************** simple.h **************************/
#ifndef SIMPLE_H
#define SIMPLE_H

#ifdef GCC
#define Inline inline
#else
#define Inline __inline
#endif

typedef unsigned short uint2;  /* two-byte integer (large arrays)      */
typedef unsigned int   uint4;  /* four-byte integers (range needed)    */
typedef unsigned int   uint;   /* fast unsigned integer, 2 or 4 bytes  */

#endif // SIMPLE_H
/********************* End simple.h ***********************/

/********************* rangecod.h *************************/
#ifndef RANGECOD_H
#define RANGECOD_H

/* The version string printed on startup */
extern char coderversion[];

typedef uint4 simz_code_value;       /* Type of a range coder value (32 bits needed) */
typedef uint4 simz_freq;             /* Frequency count type */

/* The range coder structure */
typedef struct {
    uint4 low,           /* low end of interval */
          range,         /* length of interval */
          help;          /* bytes_to_follow or intermediate value */
    unsigned char buffer;/* buffer for input/output */
    uint4 bytecount;     /* counter for output bytes */
    /* Additional fields can be added if needed */
} simz_rangecoder;

/* Prototypes for range coder functions. Their implementations
   must be provided (or linked) separately. */
void simz_start_encoding( simz_rangecoder *rc, char c, int initlength );
void simz_encode_freq( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq tot_f );
void simz_encode_shift( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq shift );
#define encode_byte(ac,b)  simz_encode_shift(ac,(simz_freq)1,(simz_freq)(b),(simz_freq)8)
#define encode_short(ac,s) simz_encode_shift(ac,(simz_freq)1,(simz_freq)(s),(simz_freq)16)

uint4 simz_done_encoding( simz_rangecoder *rc );

int simz_start_decoding( simz_rangecoder *rc );
simz_freq simz_decode_culfreq( simz_rangecoder *rc, simz_freq tot_f );
simz_freq simz_decode_culshift( simz_rangecoder *rc, simz_freq shift );
void simz_decode_update( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq tot_f );
#define decode_update_shift(rc,f1,f2,f3) simz_decode_update((rc),(f1),(f2),(simz_freq)1<<(f3))
unsigned char simz_decode_byte( simz_rangecoder *rc );
unsigned short simz_decode_short( simz_rangecoder *rc );

void simz_done_decoding( simz_rangecoder *rc );

#endif // RANGECOD_H
/******************* End rangecod.h **********************/