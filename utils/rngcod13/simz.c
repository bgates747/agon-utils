/* simz.c - Combined simple zip compressor/decompressor
   Usage:
     simz -c [infile [outfile]]   -> compress
     simz -d [infile [outfile]]   -> decompress

   (c)1999 Michael Schindler, michael@compressconsult.com
*/

#include "simz.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>
#include <stdint.h>

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
static void _simz_encode(FILE *in, FILE *out) {
    /* Compute total decompressed size */
    fseek(in, 0, SEEK_END);
    uint32_t decompressed_size = ftell(in);
    fseek(in, 0, SEEK_SET);

    /* Write the SIMZ header */
    fputc('S', out);
    fputc('I', out);
    fputc('M', out);
    fputc('Z', out);
    fputc(0, out);  /* Major version */
    fputc(9, out);  /* Minor version */
    fputc(decompressed_size & 0xFF, out);
    fputc((decompressed_size >> 8) & 0xFF, out);
    fputc((decompressed_size >> 16) & 0xFF, out);
    fputc((decompressed_size >> 24) & 0xFF, out);
    
    simz_freq counts[257], blocksize;
    simz_rangecoder rc;
    unsigned char buffer[BLOCKSIZE];
    simz_freq i;

    /* Initialize the range coder; here the first byte is 0 and no header is added */
    simz_start_encoding(&rc, 0, 0);

    while ((blocksize = (simz_freq)fread(buffer, 1, BLOCKSIZE, in)) > 0) {
        /* Write a flag (one-bit coding) to signal a new block */
        simz_encode_freq(&rc, 1, 1, 2);

        /* Build statistics for this block */
        countblock(buffer, blocksize, counts);

        /* Write the statistics (for each symbol 0..255) */
        for (i = 0; i < 256; i++)
            encode_short(&rc, counts[i]);

        /* Convert counts[] into cumulative counts.
           counts[256] is set to the block size.
           Then adjust counts[0..255] so that counts[i] is the cumulative count for all symbols less than i. */
        counts[256] = blocksize;
        for (i = 256; i > 0; i--)
            counts[i-1] = counts[i] - counts[i-1];

        /* Encode each symbol in the block using its frequency interval */
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
static void _simz_decode(FILE *in, FILE *out) {
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

    simz_rangecoder rc;
    if (simz_start_decoding(&rc) != 0) {
        fprintf(stderr, "could not successfully open input data\n");
        exit(1);
    }

    while (1) {
        /* Check for the flag that indicates a new block.
           A zero value means there are no more blocks. */
        simz_freq cf = simz_decode_culfreq(&rc, 2);
        if (cf == 0)
            break;
        simz_decode_update(&rc, 1, 1, 2);

        simz_freq counts[257], i, blocksize;
        /* Read the 256 frequency counts */
        readcounts(&rc, counts);

        /* Determine blocksize and build cumulative counts */
        blocksize = 0;
        for (i = 0; i < 256; i++) {
            simz_freq tmp = counts[i];
            counts[i] = blocksize;
            blocksize += tmp;
        }
        counts[256] = blocksize;

        /* Decode each symbol in the block */
        for (i = 0; i < blocksize; i++) {
            simz_freq cf_sym = simz_decode_culfreq(&rc, blocksize);
            simz_freq symbol = 0;
            while (counts[symbol+1] <= cf_sym)
                symbol++;
            simz_decode_update(&rc, counts[symbol+1] - counts[symbol], counts[symbol], blocksize);
            fputc((int)symbol, out);
        }
    }
    simz_done_decoding(&rc);
}

/********************** Main *****************************/

static void usage(void) {
    fprintf(stderr, "Usage: simz -c|-d [infile [outfile]]\n");
    fprintf(stderr, "   -c : compress\n");
    fprintf(stderr, "   -d : decompress\n");
    exit(1);
}

int main(int argc, char *argv[]) {
    if (argc < 2)
        usage();

    /* Redirect input and output streams if files are provided */
    if (argc >= 3) {
        if (freopen(argv[2], "rb", stdin) == NULL) {
            perror(argv[2]);
            exit(1);
        }
    }
    if (argc >= 4) {
        if (freopen(argv[3], "wb", stdout) == NULL) {
            perror(argv[3]);
            exit(1);
        }
    }

    fprintf(stderr, "%s\n", coderversion);

    if (strcmp(argv[1], "-c") == 0)
        _simz_encode(stdin, stdout);
    else if (strcmp(argv[1], "-d") == 0)
        _simz_decode(stdin, stdout);
    else
        usage();

    return 0;
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
#define outbyte(cod,x) putchar(x)
#define inbyte(cod)    getchar()

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
