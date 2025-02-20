/* simz.c - Combined simple zip compressor/decompressor
   Usage:
     simz -c [infile [outfile]]   -> compress
     simz -d [infile [outfile]]   -> decompress

   (c)1999 Michael Schindler, michael@compressconsult.com
*/

#define PY_SSIZE_T_CLEAN
#define _GNU_SOURCE

#include "simz.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>

/* Version string */
char coderversion[] = "simple zip v1.0 (c)1999 Michael Schindler";

/* Maximum block size (keep below 1<<16 to avoid overflows) */
#define BLOCKSIZE 60000

#define SIMZ_HEADER_SIZE 10

/***************** Compression Functions *****************/

/* Count occurrences of each byte in the buffer */
static void countblock(unsigned char *buffer, simz_freq length, simz_freq *counters) {
    unsigned int i;
    for (i = 0; i < 257; i++)
        counters[i] = 0;
    for (i = 0; i < length; i++)
        counters[buffer[i]]++;
}

/* Compress from input stream 'in' to output stream 'out' */
void _simz_encode_file_internal(FILE *in, FILE *out) {
    simz_rangecoder rc;
    unsigned char buffer[BLOCKSIZE];
    simz_freq counts[257], blocksize;
    simz_freq i;

    /* Determine total uncompressed size */
    fseek(in, 0, SEEK_END);
    uint32_t uncompressed_size = ftell(in);
    rewind(in);

    /* Write the SIMZ header */
    uint8_t header[SIMZ_HEADER_SIZE] = {'S', 'I', 'M', 'Z', 0, 9, 
        (uncompressed_size & 0xFF), 
        ((uncompressed_size >> 8) & 0xFF), 
        ((uncompressed_size >> 16) & 0xFF), 
        ((uncompressed_size >> 24) & 0xFF)};
    fwrite(header, 1, SIMZ_HEADER_SIZE, out);

    /* Assign the file pointers for proper I/O */
    rc.fin = in;
    rc.fout = out;

    /* Initialize the range coder */
    simz_start_encoding(&rc, 0, 0);

    while ((blocksize = (simz_freq)fread(buffer, 1, BLOCKSIZE, in)) > 0) {
        /* Write a flag (one-bit coding) to signal a new block */
        simz_encode_freq(&rc, 1, 1, 2);

        /* Build statistics for this block */
        for (i = 0; i < 257; i++) counts[i] = 0;
        for (i = 0; i < blocksize; i++) counts[buffer[i]]++;

        /* Write the frequency statistics */
        for (i = 0; i < 256; i++) encode_short(&rc, counts[i]);

        /* Convert counts[] into cumulative counts */
        counts[256] = blocksize;
        for (i = 256; i > 0; i--) counts[i - 1] = counts[i] - counts[i - 1];

        /* Encode each symbol using its frequency interval */
        for (i = 0; i < blocksize; i++) {
            int ch = buffer[i];
            simz_encode_freq(&rc, counts[ch+1] - counts[ch], counts[ch], counts[256]);
        }
    }

    /* Flag the absence of a next block */
    simz_encode_freq(&rc, 1, 0, 2);

    /* Finish encoding */
    simz_done_encoding(&rc);
}

/**************** Decompression Functions ****************/

/* Read frequency counts for the block from the range coder */
static void readcounts(simz_rangecoder *rc, simz_freq *counters) {
    int i;
    for (i = 0; i < 256; i++)
        counters[i] = simz_decode_short(rc);
}

/* Decompress from input stream 'in' to output stream 'out' */
void _simz_decode_file_internal(FILE *in, FILE *out) {
    simz_rangecoder rc;
    simz_freq counts[257], i, blocksize;

    /* Read and verify the SIMZ header */
    uint8_t header[SIMZ_HEADER_SIZE];
    if (fread(header, 1, SIMZ_HEADER_SIZE, in) != SIMZ_HEADER_SIZE) {
        fprintf(stderr, "Invalid SIMZ file: header too short\n");
        exit(1);
    }
    if (header[0] != 'S' || header[1] != 'I' || header[2] != 'M' || header[3] != 'Z') {
        fprintf(stderr, "Invalid SIMZ file: bad magic bytes\n");
        exit(1);
    }
    if (header[4] != 0 || header[5] != 9) {
        fprintf(stderr, "Unsupported SIMZ version: %d.%d\n", header[4], header[5]);
        exit(1);
    }

    uint32_t expectedOutputSize = header[6] | (header[7] << 8) | (header[8] << 16) | (header[9] << 24);

    /* Assign file pointers for proper I/O */
    rc.fin = in;
    rc.fout = out;

    if (simz_start_decoding(&rc) != 0) {
        fprintf(stderr, "Could not successfully open input data\n");
        exit(1);
    }

    uint32_t out_index = 0;
    while (out_index < expectedOutputSize) {
        /* Check for the flag that indicates a new block */
        simz_freq cf = simz_decode_culfreq(&rc, 2);
        if (cf == 0) break; // No more blocks
        simz_decode_update(&rc, 1, 1, 2);

        /* Read the 256 frequency counts */
        for (i = 0; i < 256; i++) counts[i] = simz_decode_short(&rc);

        /* Compute cumulative counts */
        blocksize = 0;
        for (i = 0; i < 256; i++) {
            simz_freq tmp = counts[i];
            counts[i] = blocksize;
            blocksize += tmp;
        }
        counts[256] = blocksize;

        /* Decode each symbol in the block */
        for (i = 0; i < blocksize && out_index < expectedOutputSize; i++) {
            simz_freq cf_sym = simz_decode_culfreq(&rc, blocksize);
            simz_freq symbol = 0;

            while (counts[symbol + 1] <= cf_sym) symbol++;
            
            simz_decode_update(&rc, counts[symbol+1] - counts[symbol], counts[symbol], blocksize);
            fputc((int)symbol, out);
            out_index++;
        }
    }

    simz_done_decoding(&rc);
}

/************** rangecod.c *****************/

/*
  define EXTRAFAST for increased speed; you loose compression and
  compatibility in exchange.
*/
#define EXTRAFAST

/* SIZE OF RANGE ENCODING CODE VALUES. */
#define CODE_BITS 32
#define Top_value ((simz_code_value)1 << (CODE_BITS-1))


/* all IO is done by these macros - change them if you want to */
/* no checking is done - do it here if you want it             */
/* cod is a pointer to the used simz_rangecoder                     */
#define outbyte(cod, x) fputc((x), (cod)->fout)
#define inbyte(cod)     fgetc((cod)->fin)

#define SHIFT_BITS (CODE_BITS - 9)
#define EXTRA_BITS ((CODE_BITS-2) % 8 + 1)
#define Bottom_value (Top_value >> 8)

#define RNGC (*rc)
#define M_outbyte(a) outbyte(rc,a)
#define M_inbyte inbyte(rc)

/* rc is the range coder to be used                            */
/* c is written as first byte in the datastream                */
/* one could do without c, but then you have an additional if  */
/* per outputbyte.                                             */
void simz_start_encoding( simz_rangecoder *rc, char c, int initlength )
{   RNGC.low = 0;                /* Full code range */
    RNGC.range = Top_value;
    RNGC.buffer = c;
    RNGC.help = 0;               /* No bytes to follow */
    RNGC.bytecount = initlength;
}

/* I do the normalization before I need a defined state instead of */
/* after messing it up. This simplifies starting and ending.       */
static Inline void simz_enc_normalize(simz_rangecoder *rc) {
    while (RNGC.range <= Bottom_value) {  /* do we need renormalisation? */
        if (RNGC.low < ((simz_code_value)0xff << SHIFT_BITS)) {  /* no carry possible --> output */
            M_outbyte(RNGC.buffer);
            while (RNGC.help > 0) {
                M_outbyte(0xff);
                RNGC.help--;
            }
            RNGC.buffer = (unsigned char)(RNGC.low >> SHIFT_BITS);
        } else if (RNGC.low & Top_value) {  /* carry now, no future carry */
            M_outbyte(RNGC.buffer + 1);
            while (RNGC.help > 0) {
                M_outbyte(0);
                RNGC.help--;
            }
            RNGC.buffer = (unsigned char)(RNGC.low >> SHIFT_BITS);
        } else {  /* passes on a potential carry */
            RNGC.help++;
        }
        RNGC.low = (RNGC.low << 8) & (Top_value - 1);
        RNGC.range <<= 8;
        RNGC.bytecount++;
    }
}

/* Encode a symbol using frequencies                         */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
/* or (faster): tot_f = (simz_code_value)1<<shift                             */
void simz_encode_freq( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq tot_f )
{	simz_code_value r, tmp;
	simz_enc_normalize( rc );
	r = RNGC.range / tot_f;
	tmp = r * lt_f;
	RNGC.low += tmp;
#ifdef EXTRAFAST
    RNGC.range = r * sy_f;
#else
    if (lt_f+sy_f < tot_f)
		RNGC.range = r * sy_f;
    else
		RNGC.range -= tmp;
#endif
}

void simz_encode_shift( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq shift )
{	simz_code_value r, tmp;
	simz_enc_normalize( rc );
	r = RNGC.range >> shift;
	tmp = r * lt_f;
	RNGC.low += tmp;
#ifdef EXTRAFAST
	RNGC.range = r * sy_f;
#else
	if ((lt_f+sy_f) >> shift)
		RNGC.range -= tmp;
	else  
		RNGC.range = r * sy_f;
#endif
}

/* Finish encoding                                           */
/* rc is the range coder to be used                          */
/* actually not that many bytes need to be output, but who   */
/* cares. I output them because decode will read them :)     */
/* the return value is the number of bytes written           */
uint4 simz_done_encoding( simz_rangecoder *rc )
{   uint tmp;
    simz_enc_normalize(rc);     /* now we have a normalized state */
    RNGC.bytecount += 5;
    if ((RNGC.low & (Bottom_value-1)) < ((RNGC.bytecount&0xffffffL)>>1))
       tmp = RNGC.low >> SHIFT_BITS;
    else
       tmp = (RNGC.low >> SHIFT_BITS) + 1;
    if (tmp > 0xff) /* we have a carry */
    {   M_outbyte(RNGC.buffer+1);
        for(; RNGC.help; RNGC.help--)
            M_outbyte(0);
    } else  /* no carry */
    {   M_outbyte(RNGC.buffer);
        for(; RNGC.help; RNGC.help--)
            M_outbyte(0xff);
    }
    M_outbyte(tmp & 0xff);
    M_outbyte((RNGC.bytecount>>16) & 0xff);
    M_outbyte((RNGC.bytecount>>8) & 0xff);
    M_outbyte(RNGC.bytecount & 0xff);
    return RNGC.bytecount;
}


/* Start the decoder                                         */
/* rc is the range coder to be used                          */
/* returns the char from simz_start_encoding or EOF               */
int simz_start_decoding( simz_rangecoder *rc )
{   int c = M_inbyte;
    if (c==EOF)
        return EOF;
    RNGC.buffer = M_inbyte;
    RNGC.low = RNGC.buffer >> (8-EXTRA_BITS);
    RNGC.range = (simz_code_value)1 << EXTRA_BITS;
    return c;
}


static Inline void simz_dec_normalize( simz_rangecoder *rc )
{   while (RNGC.range <= Bottom_value)
    {   RNGC.low = (RNGC.low<<8) | ((RNGC.buffer<<EXTRA_BITS)&0xff);
        RNGC.buffer = M_inbyte;
        RNGC.low |= RNGC.buffer >> (8-EXTRA_BITS);
        RNGC.range <<= 8;
    }
}

/* Calculate culmulative frequency for next symbol. Does NO update!*/
/* rc is the range coder to be used                          */
/* tot_f is the total frequency                              */
/* or: totf is (simz_code_value)1<<shift                                      */
/* returns the culmulative frequency                         */
simz_freq simz_decode_culfreq( simz_rangecoder *rc, simz_freq tot_f )
{   simz_freq tmp;
    simz_dec_normalize(rc);
    RNGC.help = RNGC.range/tot_f;
    tmp = RNGC.low/RNGC.help;
#ifdef EXTRAFAST
    return tmp;
#else
    return (tmp>=tot_f ? tot_f-1 : tmp);
#endif
}

simz_freq simz_decode_culshift( simz_rangecoder *rc, simz_freq shift )
{   simz_freq tmp;
    simz_dec_normalize(rc);
    RNGC.help = RNGC.range>>shift;
    tmp = RNGC.low/RNGC.help;
#ifdef EXTRAFAST
    return tmp;
#else
    return (tmp>>shift ? ((simz_code_value)1<<shift)-1 : tmp);
#endif
}


/* Update decoding state                                     */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
void simz_decode_update( simz_rangecoder *rc, simz_freq sy_f, simz_freq lt_f, simz_freq tot_f)
{   simz_code_value tmp;
    tmp = RNGC.help * lt_f;
    RNGC.low -= tmp;
#ifdef EXTRAFAST
    RNGC.range = RNGC.help * sy_f;
#else
    if (lt_f + sy_f < tot_f)
        RNGC.range = RNGC.help * sy_f;
    else
        RNGC.range -= tmp;
#endif
}


/* Decode a byte/short without modelling                     */
/* rc is the range coder to be used                          */
unsigned char simz_decode_byte(simz_rangecoder *rc)
{   unsigned char tmp = simz_decode_culshift(rc,8);
    simz_decode_update( rc,1,tmp,(simz_freq)1<<8);
    return tmp;
}

unsigned short simz_decode_short(simz_rangecoder *rc)
{   unsigned short tmp = simz_decode_culshift(rc,16);
    simz_decode_update( rc,1,tmp,(simz_freq)1<<16);
    return tmp;
}


/* Finish decoding                                           */
/* rc is the range coder to be used                          */
void simz_done_decoding( simz_rangecoder *rc )
{   simz_dec_normalize(rc);      /* normalize to use up all bytes */
}


// ===================================================
// Python C-extension entry points:
// ---------------------------------------------------
/* 
 * simz_encode()
 * Python wrapper for _simz_encode_file_internal().
 * Expects two string arguments: the input file path and the output file path.
 */
PyObject *simz_encode(PyObject *self, PyObject *args) {
    const char *in_filename;
    const char *out_filename;
    
    if (!PyArg_ParseTuple(args, "ss", &in_filename, &out_filename)) {
        return NULL;
    }
    
    FILE *infile = fopen(in_filename, "rb");
    if (!infile) {
        PyErr_Format(PyExc_IOError, "Could not open input file '%s'", in_filename);
        return NULL;
    }
    
    FILE *outfile = fopen(out_filename, "wb");
    if (!outfile) {
        fclose(infile);
        PyErr_Format(PyExc_IOError, "Could not open output file '%s'", out_filename);
        return NULL;
    }
    
    /* Call the compressor routine (defined in your simz code) */
    _simz_encode_file_internal(infile, outfile);
    
    fclose(infile);
    fclose(outfile);
    
    Py_RETURN_NONE;
}

/* 
 * simz_decode()
 * Python wrapper for _simz_decode_file_internal().
 * Expects two string arguments: the input file path and the output file path.
 */
PyObject *simz_decode(PyObject *self, PyObject *args) {
    const char *in_filename;
    const char *out_filename;
    
    if (!PyArg_ParseTuple(args, "ss", &in_filename, &out_filename)) {
        return NULL;
    }
    
    FILE *infile = fopen(in_filename, "rb");
    if (!infile) {
        PyErr_Format(PyExc_IOError, "Could not open input file '%s'", in_filename);
        return NULL;
    }
    
    FILE *outfile = fopen(out_filename, "wb");
    if (!outfile) {
        fclose(infile);
        PyErr_Format(PyExc_IOError, "Could not open output file '%s'", out_filename);
        return NULL;
    }
    
    /* Call the decompressor routine (defined in your simz code) */
    _simz_decode_file_internal(infile, outfile);
    
    fclose(infile);
    fclose(outfile);
    
    Py_RETURN_NONE;
}

/* 
 * simz_encode_bytes()
 * Python wrapper for in-memory compression.
 * Accepts one bytes object (the raw data),
 * returns a bytes object (the compressed data).
 */
PyObject *simz_encode_bytes(PyObject *self, PyObject *args) {
    const char *in_data = NULL;
    Py_ssize_t in_len = 0;

    /* Parse Python arguments: y# means "read a bytes-like object" */
    if (!PyArg_ParseTuple(args, "y#", &in_data, &in_len)) {
        return NULL;
    }

    /* Create a memory stream from the input data */
    FILE *in_mem = fmemopen((void *)in_data, (size_t)in_len, "rb");
    if (!in_mem) {
        PyErr_SetString(PyExc_RuntimeError, "Unable to open input memory stream.");
        return NULL;
    }

    /* Create a memory stream to capture the compressed output */
    char *out_buf = NULL;
    size_t out_size = 0;
    FILE *out_mem = open_memstream(&out_buf, &out_size);
    if (!out_mem) {
        fclose(in_mem);
        PyErr_SetString(PyExc_RuntimeError, "Unable to open output memory stream.");
        return NULL;
    }

    /* Reuse the file-based compressor logic, but with our memory streams */
    _simz_encode_file_internal(in_mem, out_mem);

    fclose(in_mem);
    fclose(out_mem);

    /* Create a Python bytes object from the in-memory compressed data */
    PyObject *result = PyBytes_FromStringAndSize(out_buf, out_size);
    free(out_buf);   /* open_memstream() allocated this buffer */

    return result;
}

/* 
 * simz_decode_bytes()
 * Python wrapper for in-memory decompression.
 * Accepts one bytes object (the compressed data),
 * returns a bytes object (the decompressed data).
 */
PyObject *simz_decode_bytes(PyObject *self, PyObject *args) {
    const char *in_data = NULL;
    Py_ssize_t in_len = 0;

    if (!PyArg_ParseTuple(args, "y#", &in_data, &in_len)) {
        return NULL;
    }

    /* Create a memory stream from the compressed input data */
    FILE *in_mem = fmemopen((void *)in_data, (size_t)in_len, "rb");
    if (!in_mem) {
        PyErr_SetString(PyExc_RuntimeError, "Unable to open input memory stream.");
        return NULL;
    }

    /* Create a memory stream to capture the decompressed output */
    char *out_buf = NULL;
    size_t out_size = 0;
    FILE *out_mem = open_memstream(&out_buf, &out_size);
    if (!out_mem) {
        fclose(in_mem);
        PyErr_SetString(PyExc_RuntimeError, "Unable to open output memory stream.");
        return NULL;
    }

    /* Reuse the file-based decompressor logic, but with memory streams */
    _simz_decode_file_internal(in_mem, out_mem);

    fclose(in_mem);
    fclose(out_mem);

    /* Create a Python bytes object from the decompressed data */
    PyObject *result = PyBytes_FromStringAndSize(out_buf, out_size);
    free(out_buf);

    return result;
}
