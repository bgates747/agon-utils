#ifndef SIMZ_H
#define SIMZ_H

#include <Python.h>

#ifdef __cplusplus
extern "C" {
#endif

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

/* Type definitions for range coder */
typedef uint4 simz_code_value;       /* Type of a range coder value (32 bits needed) */
typedef uint4 simz_freq;             /* Frequency count type */

/* The range coder structure */
typedef struct {
    uint4 low;           /* Low end of interval */
    uint4 range;         /* Length of interval */
    uint4 help;          /* Bytes_to_follow or intermediate value */
    unsigned char buffer;/* Buffer for input/output */
    uint4 bytecount;     /* Counter for output bytes */

    /* Add these two fields so we can store actual file pointers */
    FILE *fin;           /* Pointer to input file */
    FILE *fout;          /* Pointer to output file */
} simz_rangecoder;

/* Prototypes for range coder functions */
void simz_start_encoding(simz_rangecoder *rc, char c, int initlength);
void simz_encode_freq(simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq tot_f);
void simz_encode_shift(simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq shift);
#define encode_byte(ac, b)  simz_encode_shift(ac, (simz_freq)1, (simz_freq)(b), (simz_freq)8)
#define encode_short(ac, s) simz_encode_shift(ac, (simz_freq)1, (simz_freq)(s), (simz_freq)16)

uint4 simz_done_encoding(simz_rangecoder *rc);

int simz_start_decoding(simz_rangecoder *rc);
simz_freq simz_decode_culfreq(simz_rangecoder *rc, simz_freq tot_f);
simz_freq simz_decode_culshift(simz_rangecoder *rc, simz_freq shift);
void simz_decode_update(simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq tot_f);
#define simz_decode_update_shift(rc, f1, f2, f3) simz_decode_update((rc), (f1), (f2), (simz_freq)1 << (f3))
unsigned char simz_decode_byte(simz_rangecoder *rc);
unsigned short simz_decode_short(simz_rangecoder *rc);

void simz_done_decoding(simz_rangecoder *rc);

/* Prototypes for simz compression and decompression */
void _simz_encode_file_internal(FILE *in, FILE *out);
void _simz_decode_file_internal(FILE *in, FILE *out);

// ===================================================
// Prototypes for the Python C-extension entry points:
// ---------------------------------------------------
/**
 * Compress a file using the simz encoder.
 * Python call signature: `simz_encode(input_file: str, output_file: str) -> None`
 * 
 * Arguments:
 *   - input_file: Path to the input file (string)
 *   - output_file: Path to the output file (string)
 */
PyObject *simz_encode(PyObject *self, PyObject *args);

/**
 * Decompress a file using the simz decoder.
 * Python call signature: `simz_decode(input_file: str, output_file: str) -> None`
 * 
 * Arguments:
 *   - input_file: Path to the input file (string)
 *   - output_file: Path to the output file (string)
 */
PyObject *simz_decode(PyObject *self, PyObject *args);

/**
 * Compress a Python bytes object (in memory) and return a bytes object.
 * Python call signature: `simz_encode_bytes(data: bytes) -> bytes`
 */
PyObject *simz_encode_bytes(PyObject *self, PyObject *args);

/**
 * Decompress a Python bytes object (in memory) and return a bytes object.
 * Python call signature: `simz_decode_bytes(data: bytes) -> bytes`
 */
PyObject *simz_decode_bytes(PyObject *self, PyObject *args);

#ifdef __cplusplus
}
#endif

#endif /* SIMZ_H */
