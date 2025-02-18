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

/* The version string printed on startup */
extern char coderversion[];

typedef uint4 code_value;       /* Type of a range coder value (32 bits needed) */
typedef uint4 freq;             /* Frequency count type */

/* The range coder structure */
typedef struct {
    uint4 low,           /* low end of interval */
          range,         /* length of interval */
          help;          /* bytes_to_follow or intermediate value */
    unsigned char buffer;/* buffer for input/output */
    uint4 bytecount;     /* counter for output bytes */
    /* Additional fields can be added if needed */
} rangecoder;

/* Prototypes for range coder functions. */
void start_encoding( rangecoder *rc, char c, int initlength );
void encode_freq( rangecoder *rc, freq sy_f, freq lt_f, freq tot_f );
void encode_shift( rangecoder *rc, freq sy_f, freq lt_f, freq shift );
#define encode_byte(ac,b)  encode_shift(ac,(freq)1,(freq)(b),(freq)8)
#define encode_short(ac,s) encode_shift(ac,(freq)1,(freq)(s),(freq)16)

uint4 done_encoding( rangecoder *rc );

int start_decoding( rangecoder *rc );
freq decode_culfreq( rangecoder *rc, freq tot_f );
freq decode_culshift( rangecoder *rc, freq shift );
void decode_update( rangecoder *rc, freq sy_f, freq lt_f, freq tot_f );
#define decode_update_shift(rc,f1,f2,f3) decode_update((rc),(f1),(f2),(freq)1<<(f3))
unsigned char decode_byte( rangecoder *rc );
unsigned short decode_short( rangecoder *rc );

void done_decoding( rangecoder *rc );

#endif // SIMPLE_H
