#ifndef RANGECOD_H
#define RANGECOD_H

#ifdef __cplusplus
extern "C" {
#endif

#include "simz.h"

/* The version string printed on startup */
extern char coderversion[];

/* Type definitions */
typedef uint4 code_value;       /* 32-bit range coder value */
typedef uint4 freq;             /* Frequency count type */

/* The range coder structure for memory-based I/O */
typedef struct {
    code_value low;           /* low end of interval */
    code_value range;         /* length of interval */
    code_value help;          /* bytes_to_follow or intermediate value */
    unsigned char buffer;     /* temporary output byte buffer */
    uint4 bytecount;          /* counter for output bytes */
    /* Memory output buffer fields: */
    unsigned char *out_buffer;/* pointer to the output buffer */
    size_t out_capacity;      /* total capacity of out_buffer */
    size_t out_pos;           /* current write position in out_buffer */
} rangecoder;

/* Prototypes for the range coder functions (memory based). 
   Their implementations below use the internal output buffer rather than putchar/getchar.
*/
void start_encoding(rangecoder *rc, unsigned char *out_buffer, size_t out_capacity);
void encode_freq(rangecoder *rc, freq sy_f, freq lt_f, freq tot_f);
void encode_shift(rangecoder *rc, freq sy_f, freq lt_f, freq shift);
#define encode_byte(ac,b)  encode_shift(ac,(freq)1,(freq)(b),(freq)8)
#define encode_short(ac,s) encode_shift(ac,(freq)1,(freq)(s),(freq)16)

uint4 done_encoding(rangecoder *rc);

int start_decoding(rangecoder *rc, const unsigned char *in_buffer, size_t in_capacity);
freq decode_culfreq(rangecoder *rc, freq tot_f);
freq decode_culshift(rangecoder *rc, freq shift);
void decode_update(rangecoder *rc, freq sy_f, freq lt_f, freq tot_f);
#define decode_update_shift(rc,f1,f2,f3) decode_update((rc),(f1),(f2),(freq)1<<(f3))
unsigned char decode_byte(rangecoder *rc);
unsigned short decode_short(rangecoder *rc);

void done_decoding(rangecoder *rc);

#ifdef __cplusplus
}
#endif

#endif // RANGECOD_H
