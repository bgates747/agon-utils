#include "szip.h"

/*
  bitmodel.c     bit indexed trees probability model

  (c) Michael Schindler
  1997, 1998
  http://www.compressconsult.com or http://eiunix.tuwien.ac.at/~michael
  michael@compressconsult.com       michael@eiunix.tuwien.ac.at

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

// #include "bitmodel.h"
#include <stdio.h>     /* NULL */
#include <stdlib.h>    /* malloc, free */


/* constructs the b_i_t structire */
static Inline void build_cf(bitmodel *m)
{   int i;
    uint2 *cf;
    cf = m->cf;
    m->totalfreq = 0;
    for (i=1; i<=m->n; i<<=1)
    {   int j;
        for (j=i; j<=m->n; j+= i<<1)
        {   int k;
#ifdef EXCLUDEONUPDATE
            if (m->f[j-1] & 0x8000)
                cf[j] = 0;
            else
#endif
                m->totalfreq += cf[j] = m->f[j-1];
            for (k=i>>1; k; k>>=1)
                cf[j] += cf[j-k];
        } /* end for j */
    } /* end for i */
}


/* scales the culmulative frequency tables by 0.5 and keeps nonzero values */
void scalefreqbitmod(bitmodel *m)
{   uint2 *f, *endf;
    for (f=m->f, endf = f+m->n; f<endf; f++)
#ifdef EXCLUDEONUPDATE
        *f = ((1+(*f & 0x7fff))>>1) | (*f & 0x8000);
#else
        *f = (1 + *f)>>1;
#endif
    build_cf(m);
}


/* initialisation of bitmodel                          */
/* m   bitmodel to be initialized                      */
/* n   number of symbols in that model                 */
/* max_totf  maximum allowed total frequency count     */
/* rescale  desired rescaling interval, must be <max_totf/2 */
/* init  array of int's to be used for initialisation (NULL ok) */
void initbitmodel( bitmodel *m, int n, int max_totf, int rescale,
    int *init )
{   m->n = n;
    if (max_totf < n<<1) max_totf = n<<1;
    m->max_totf = max_totf;
    m->incr = max_totf/2/rescale;
    if (m->incr < 1) m->incr = 1;
    m->f = (uint2*) malloc(n*sizeof(uint2));
    m->cf = (uint2*) malloc((n+1)*sizeof(uint2));
    m->mask = 1;
    while (n>>=1)
        m->mask <<=1;
    resetbitmodel(m,init);
}



/* reinitialisation of bitmodel                        */
/* m   bitmodel to be initialized                      */
/* init  array of int's to be used for initialisation (NULL ok) */
void resetbitmodel( bitmodel *m, int *init)
{   int i;
    if (init == NULL)
    {   for(i=0; i<m->n; i++)
            m->f[i] = 1;
        m->totalfreq = m->n;
    } else
    {   m->totalfreq = 0;
        for(i=0; i<m->n; i++)
        {   m->f[i] = init[i];
            m->totalfreq += init[i];
        }
    }
    while (m->totalfreq > m->max_totf)
        scalefreqbitmod(m);
    build_cf(m);
}


/* deletion of bitmodel m                              */
void deletebitmodel( bitmodel *m )
{   free(m->f);
    free(m->cf);
    m->n = 0;
}


/* retrieval of estimated frequencies for a symbol     */
/* m   bitmodel to be questioned                       */
/* sym  symbol for which data is desired; must be <n   */
/* sy_f frequency of that symbol                       */
/* lt_f frequency of all smaller symbols together      */
/* the total frequency can be obtained with bit_totf   */
void bitgetfreq( bitmodel *m, int sym, int *sy_f, int *lt_f)
{   int cul;
    uint2 *cf;
    *sy_f = m->f[sym];
    sym++;
    cf = m->cf;
    cul = cf[sym];
    while (sym &= sym-1)
        cul += cf[sym];
    *lt_f = cul - *sy_f;
}


/* find out symbol for a given cumulative frequency    */
/* m   bitmodel to be questioned                       */
/* lt_f  cumulative frequency                          */
int bitgetsym( bitmodel *m, int lt_f )
{   int sym, mask, n;
    uint2 *cf;
    mask = m->mask;
    n = m->n;
    cf = m->cf;
    sym = 0;
    do
    {   int x;
        if ((x=sym|mask) <= n && lt_f >= cf[x])
        {   lt_f -= cf[x];
            sym = x;
        }
    } while (mask >>= 1);
    return sym;
}


/* update the cumulative frequency data by delta */
static Inline void bit_cfupd( bitmodel *m, int sym, int delta )
{   m->totalfreq += delta;
    if (m->totalfreq > m->max_totf)
        scalefreq(m);
    else
    {   uint2 *cf;
        sym++;
        cf = m->cf;
        while (sym<= m->n)
        {   cf[sym] += delta;
            sym = (sym | (sym-1)) + 1;
        }
    }
}


/* update model                                        */
/* m   bitmodel to be updated                          */
/* sym  symbol that occurred (must be <n from init)    */
void bitupdate( bitmodel *m, int sym )
{   m->f[sym] += m->incr;
    bit_cfupd(m, sym, m->incr);
}


#ifdef EXCLUDEONUPDATE
/* update model and exclude symbol                     */
/* m   bitmodel to be updated                          */
/* sym  symbol that occurred (must be <n from init)    */
void bitupdate_ex( bitmodel *m, int sym )
{   int delta;
    delta = -m->f[sym];
    m->f[sym] = (m->f[sym] + m->incr) | 0x8000;
    bit_cfupd(m, sym, delta);
}


/* deactivate symbol                                   */
/* m   bitmodel to be updated                          */
/* sym  symbol to be reactivated                       */
void bitdeactivate( bitmodel *m, int sym )
{   bit_cfupd(m, sym, -m->f[sym]);
    m->f[sym] |= 0x8000;
}


/* reactivate symbol                                   */
/* m   bitmodel to be updated                          */
/* sym  symbol to be reactivated                       */
void bitreactivate( bitmodel *m, int sym )
{   m->f[sym] &= 0x7fff;
    bit_cfupd(m, sym, m->f[sym]);
}
#endif

/* check.c - checks stdin for equality with a given file,
reports filename to logfile if not equal */

#include <stdio.h>
#include <stdlib.h>
#ifndef unix
// #include <io.h>
#include <fcntl.h>
#endif

void usage()
{	fprintf(stderr,"check <otherfile> <logfile>\n");
	exit(2);
}


void bugfound(char *filename, char *logfilename)
{   FILE *logfil;
    logfil = fopen( logfilename, "ab" );
    fprintf(logfil,"%s\n",filename);
    fclose(logfil);
    exit(1);
}

int main( int argc, char *argv[] )
{   FILE *infil;
    int ch;
    if (argc!=3) usage();

    infil = fopen( argv[1], "rb" );
    if (infil==NULL) bugfound(argv[1],argv[2]);


#ifndef unix
    setmode( fileno( infil ), O_BINARY );
    setmode( fileno( stdin ), O_BINARY );
#endif

    while ((ch=getchar()) != EOF)
        if (getc(infil) != ch)
        {   fclose(infil);
            bugfound(argv[1],argv[2]);
        }
    if (getc(infil) != EOF)
        {   fclose(infil);
            bugfound(argv[1],argv[2]);
        }
    return 0;
}

// #include "rangecod.c"
// #include "qsmodel.c"
// #include "bitmodel.c"
// #include "sz_mod4.c"
// #include "szip.c"
// #include "sz_srt.c"
// #include "reorder.c"

/* extract.c - extracts buggy datablocks for szip 1.10 */

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#ifndef unix
// #include <io.h>
#include <fcntl.h>
#endif

void usage()
{	fprintf(stderr,"extract [blocksize] originalfile corruptfile logfile [errorblockfile]\n");
    fprintf(stderr,"the blocksize must be the same as used with szip (example: -b1)\n");
	exit(2);
}

int readnum(char *s, int min, int max)
{	int j=0;
	while (isdigit(*s))
	{	j=10*j+*s-'0';
		s++;
	}
	if (j<min || j>max)
		usage();
	return j;
}


void bugfound(unsigned char *buffer, size_t bufsize, char *logfilename,
char *blockfilename)
{   FILE *blockfil;
    size_t writebytes;
    blockfil = fopen( logfilename, "ab" );
    fprintf(blockfil,"%s\n",blockfilename);
    fclose(blockfil);
    blockfil = fopen( blockfilename, "wb" );
#ifndef unix
    setmode( fileno( blockfil ), O_BINARY );
#endif
    writebytes = fwrite( (char *)buffer, 1, (size_t)bufsize, blockfil);
    fclose(blockfil);
    if (writebytes==bufsize)
        exit(1);
    else
        exit(2);
}


size_t blocksize=1703936;

int main( int argc, char *argv[] )
{   unsigned char *infilename=NULL, *outfilename=NULL,
        *blockfilename=NULL, *logfilename=NULL, *buffer;
    FILE *infil, *outfil;
    size_t i, bufsize;

    for (i=1; i<(unsigned)argc; i++)
	{	char *s=argv[i];
	    if (*s == '-')
		{	s++;
			if (*s=='b')
                blocksize = (100000*readnum(s+1,1,41)+0x7fff) & 0x7fff8000L;
            else
                usage();
        }
		else if (infilename == NULL)
			infilename = s;
		else if (outfilename == NULL)
			outfilename = s;
		else if (logfilename == NULL)
			logfilename = s;
		else if (blockfilename == NULL)
			blockfilename = s;
		else
			usage();
	}
    if (logfilename==NULL)
        usage();

    infil = fopen( infilename, "rb" );
    outfil = fopen( outfilename, "rb" );

#ifndef unix
    setmode( fileno( infil ), O_BINARY );
    setmode( fileno( outfil ), O_BINARY );
#endif

    buffer = (unsigned char*) malloc(blocksize);
    do
    {   bufsize = fread( (char *)buffer, 1, (size_t)blocksize, infil);
        for (i=0; i<bufsize; i++)
            if (buffer[i] != getc(outfil))
            {   fclose(infil);
                fclose(outfil);
                // bugfound(buffer,bufsize,logfilename,blockfilename);
                bugfound(logfilename,blockfilename);
            }
    } while (bufsize==blocksize);
    fclose(infil);
    fclose(outfil);
    return 0;
}

/*
  qsmodel.c     headerfile for quasistatic probability model

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

// #include "qsmodel.h"
#include <stdio.h>
#include <stdlib.h>

/* default tablesize 1<<TBLSHIFT */
#define TBLSHIFT 7

/* rescale frequency counts */
static void dorescale( qsmodel *m)
{   int i, cf, missing;
    if (m->nextleft)  /* we have some more before actual rescaling */
    {   m->incr++;
        m->left = m->nextleft;
        m->nextleft = 0;
        return;
    }
    if (m->rescale < m->targetrescale)  /* double rescale interval if needed */
    {   m->rescale <<= 1;
        if (m->rescale > m->targetrescale)
            m->rescale = m->targetrescale;
    }
    cf = missing = m->cf[m->n];  /* do actual rescaling */
    for(i=m->n-1; i; i--)
    {   int tmp = m->newf[i];
        cf -= tmp;
        m->cf[i] = cf;
        tmp = tmp>>1 | 1;
        missing -= tmp;
        m->newf[i] = tmp;
    }
    if (cf!=m->newf[0])
    {   fprintf(stderr,"BUG: rescaling left %d total frequency\n",cf);
        deleteqsmodel(m);
        exit(1);
    }
    m->newf[0] = m->newf[0]>>1 | 1;
    missing -= m->newf[0];
    m->incr = missing / m->rescale;
    m->nextleft = missing % m->rescale;
    m->left = m->rescale - m->nextleft;
    if (m->search != NULL)
    {   i=m->n;
        while (i)
        {   int start, end;
            end = (m->cf[i]-1) >> m->searchshift;
            i--;
            start = m->cf[i] >> m->searchshift;
            while (start<=end)
            {   m->search[start] = i;
                start++;
            }
        }
    }
}


/* initialisation of qsmodel                           */
/* m   qsmodel to be initialized                       */
/* n   number of symbols in that model                 */
/* lg_totf  base2 log of total frequency count         */
/* rescale  desired rescaling interval, should be < 1<<(lg_totf+1) */
/* init  array of int's to be used for initialisation (NULL ok) */
/* compress  set to 1 on compression, 0 on decompression */
void initqsmodel( qsmodel *m, int n, int lg_totf, int rescale, int *init, int compress )
{   m->n = n;
    m->targetrescale = rescale;
    m->searchshift = lg_totf - TBLSHIFT;
    if (m->searchshift < 0)
        m->searchshift = 0;
    m->cf = (uint2*) malloc((n+1)*sizeof(uint2));
    m->newf = (uint2*) malloc((n+1)*sizeof(uint2));
    m->cf[n] = 1<<lg_totf;
    m->cf[0] = 0;
    if (compress)
        m->search = NULL;
    else
    {   m->search = (uint2*) malloc(((1<<TBLSHIFT)+1)*sizeof(uint2));
        m->search[1<<TBLSHIFT] = n-1;
    }
    resetqsmodel(m, init);
}


/* reinitialisation of qsmodel                         */
/* m   qsmodel to be initialized                       */
/* init  array of int's to be used for initialisation (NULL ok) */
void resetqsmodel( qsmodel *m, int *init)
{   int i, end, initval;
    m->rescale = m->n>>4 | 2;
    m->nextleft = 0;
    if (init == NULL)
    {   initval = m->cf[m->n] / m->n;
        end = m->cf[m->n] % m->n;
        for (i=0; i<end; i++)
            m->newf[i] = initval+1;
        for (; i<m->n; i++)
            m->newf[i] = initval;
    } else
        for(i=0; i<m->n; i++)
            m->newf[i] = init[i];
    dorescale(m);
}


/* deletion of qsmodel m                               */
void deleteqsmodel( qsmodel *m )
{   free(m->cf);
    free(m->newf);
    if (m->search != NULL)
        free(m->search);
}


/* retrieval of estimated frequencies for a symbol     */
/* m   qsmodel to be questioned                        */
/* sym  symbol for which data is desired; must be <n   */
/* sy_f frequency of that symbol                       */
/* lt_f frequency of all smaller symbols together      */
/* the total frequency is 1<<lg_totf                   */
void qsgetfreq( qsmodel *m, int sym, int *sy_f, int *lt_f )
{   *sy_f = m->cf[sym+1] - (*lt_f = m->cf[sym]);
}	


/* find out symbol for a given cumulative frequency    */
/* m   qsmodel to be questioned                        */
/* lt_f  cumulative frequency                          */
int qsgetsym( qsmodel *m, int lt_f )
{   int lo, hi;
    uint2 *tmp;
    tmp = m->search+(lt_f>>m->searchshift);
    lo = *tmp;
    hi = *(tmp+1) + 1;
    while (lo+1 < hi )
    {   int mid = (lo+hi)>>1;
        if (lt_f < m->cf[mid])
            hi = mid;
        else
            lo = mid;
    }
    return lo;
}


/* update model                                        */
/* m   qsmodel to be updated                           */
/* sym  symbol that occurred (must be <n from init)    */
void qsupdate( qsmodel *m, int sym )
{   if (m->left <= 0)
        dorescale(m);
    m->left--;
    m->newf[sym] += m->incr;
}

// #include "port.h"
#include <stdlib.h>

#define swap(x,y) {uint4 tmp = *(x); *(x) = *(y); *(y) = tmp;}


/* prototypes for local routines */
void shortsort ( uint4 *lo, uint4 *hi, unsigned char *data, uint4 minmatch );

static Inline int qscmp(uint4 a, uint4 b, unsigned char *data, uint4 *ml)
{	unsigned char *a1,*b1;
    a1 = data + a;
	b1 = data + b;
	while (a1 > data && *a1 == *b1)
	{	a1--; b1--;
	}
	*ml = data+a-a1;
	if (*a1 <= *b1)
			return -1;
	return 1;
}

static int qscompare(uint4 a, uint4 b, unsigned char *data, uint4 *ml)
{	if (a<b)
		return qscmp(a,b,data,ml);
	else 
		return -qscmp(b,a,data,ml);
}

// never used but we leave here for reference
// static void checksort(uint4 *lo, uint4 *hi, unsigned char *data)
// {   uint4 ml;
//     while(lo<hi)
//     {   if (qscompare(*lo,*(lo+1),data,&ml)!= -1)
//             ml=1;
//         lo++;
//     }
// }        


/* this parameter defines the cutoff between using quick sort and
   insertion sort for arrays; arrays with lengths shorter or equal to the
   below value use insertion sort */

#define CUTOFF 8            /* testing shows that this is good value */


/***
*qsort(base, num, wid, comp) - quicksort function for sorting arrays
*
*Purpose:
*       quicksort the array of elements
*       side effects:  sorts in place
*
*Entry:
*       char *base = pointer to base of array
*       unsigned num  = number of elements in the array
*       unsigned width = width in bytes of each array element
*       int (*comp)() = pointer to function returning analog of strcmp for
*               strings, but supplied by user for comparing the array elements.
*               it accepts 2 pointers to elements and returns neg if 1<2, 0 if
*               1=2, pos if 1>2.
*
*Exit:
*       returns void
*
*Exceptions:
*
*******************************************************************************/

/* sort the array between lo and hi (inclusive) */

static void qsort_u4 ( uint4 *base, uint4 num, unsigned char *data, uint4 minmatch )
{
    uint4 *lo, *hi;             /* ends of sub-array currently sorting */
    uint4 *mid;                 /* points to middle of subarray */
    uint4 *loguy, *higuy;       /* traveling pointers for partition step */
    uint4 size;                 /* size of the sub-array */
    uint4 *lostk[30], *histk[30], mm[30];
	uint4 lomm, himm;			/* minmatch for low/high */
    int stkptr;                 /* stack for saving sub-array to be processed */

    /* Note: the number of stack entries required is no more than
       1 + log2(size), so 30 is sufficient for any array */

    if (num < 2)
        return;                 /* nothing to do */

    stkptr = 0;                 /* initialize stack */

    lo = base;
    hi = base + (num-1);        /* initialize limits */

    /* this entry point is for pseudo-recursion calling: setting
       lo and hi and jumping to here is like recursion, but stkptr is
       prserved, locals aren't, so we preserve stuff on the stack */
recurse:

    size = (hi - lo) + 1;        /* number of el's to sort */

    /* below a certain size, it is faster to use a O(n^2) sorting method */
    if (size <= CUTOFF) {
         shortsort(lo, hi, data, minmatch);
    }
    else {
		uint4 ml;
        /* First we pick a partititioning element.  The efficiency of the
           algorithm demands that we find one that is approximately the
           median of the values, but also that we select one fast.  Using
           the first one produces bad performace if the array is already
           sorted, so we use the middle one, which would require a very
           wierdly arranged array for worst case performance.  Testing shows
           that a median-of-three algorithm does not, in general, increase
           performance. */

        mid = lo + rand()%size;     /* find middle element */
        swap(mid, lo)               /* swap it to beginning of array */

        /* We now wish to partition the array into three pieces, one
           consisiting of elements <= partition element, one of elements
           equal to the parition element, and one of element >= to it.  This
           is done below; comments indicate conditions established at every
           step. */

        loguy = lo;
        higuy = hi + 1;
		lomm = num-minmatch;
		himm = num-minmatch;
		ml = num-minmatch;

        /* Note that higuy decreases and loguy increases on every iteration,
           so loop must terminate. */
        for (;;) {
            /* lo <= loguy < hi, lo < higuy <= hi + 1,
               A[i] <= A[lo] for lo <= i <= loguy,
               A[i] >= A[lo] for higuy <= i <= hi */

            do  {
				if (ml<lomm) lomm = ml;
                loguy ++;
            } while (loguy <= hi && qscompare(*loguy-minmatch,*lo-minmatch,data,&ml) <= 0);

            /* lo < loguy <= hi+1, A[i] <= A[lo] for lo <= i < loguy,
               either loguy > hi or A[loguy] > A[lo] */

            do  {
				if (ml<himm) himm = ml;
                higuy --;
            } while (higuy > lo && qscompare(*higuy-minmatch,*lo-minmatch,data,&ml ) >= 0);

            /* lo-1 <= higuy <= hi, A[i] >= A[lo] for higuy < i <= hi,
               either higuy <= lo or A[higuy] < A[lo] */

            if (higuy < loguy)
                break;

            /* if loguy > hi or higuy <= lo, then we would have exited, so
               A[loguy] > A[lo], A[higuy] < A[lo],
               loguy < hi, highy > lo */

            swap(loguy, higuy)

            /* A[loguy] < A[lo], A[higuy] > A[lo]; so condition at top
               of loop is re-established */
        }
		if (ml<lomm) lomm = ml;

		
        /*     A[i] >= A[lo] for higuy < i <= hi,
               A[i] <= A[lo] for lo <= i < loguy,
               higuy < loguy, lo <= higuy <= hi
           implying:
               A[i] >= A[lo] for loguy <= i <= hi,
               A[i] <= A[lo] for lo <= i <= higuy,
               A[i] = A[lo] for higuy < i < loguy */

        swap(lo, higuy)     /* put partition element in place */

        /* OK, now we have the following:
              A[i] >= A[higuy] for loguy <= i <= hi,
              A[i] <= A[higuy] for lo <= i < higuy
              A[i] = A[lo] for higuy <= i < loguy    */

        /* We've finished the partition, now we want to sort the subarrays
           [lo, higuy-1] and [loguy, hi].
           We do the smaller one first to minimize stack usage.
           We only sort arrays of length 2 or more.*/

        if ( higuy - 1 - lo >= hi - loguy ) {
            if (lo + 1 < higuy) {
                lostk[stkptr] = lo;
                histk[stkptr] = higuy - 1;
				mm[stkptr] = lomm+minmatch;
                ++stkptr;
            }                           /* save big recursion for later */

            if (loguy < hi) {
                lo = loguy;
				minmatch += himm;
                goto recurse;           /* do small recursion */
            }
        }
        else {
            if (loguy < hi) {
                lostk[stkptr] = loguy;
                histk[stkptr] = hi;
				mm[stkptr] = himm+minmatch;
                ++stkptr;               /* save big recursion for later */
            }

            if (lo + 1 < higuy) {
                hi = higuy - 1;
				minmatch += lomm;
                goto recurse;           /* do small recursion */
            }
        }
    }

    /* We have sorted the array, except for any pending sorts on the stack.
       Check if there are any, and do them. */

    --stkptr;
    if (stkptr >= 0) {
        lo = lostk[stkptr];
        hi = histk[stkptr];
		minmatch = mm[stkptr];
        goto recurse;           /* pop subarray from stack */
    }
    else
        return;                 /* all subarrays done */
}


/***
*shortsort(hi, lo, width, comp) - insertion sort for sorting short arrays
*
*Purpose:
*       sorts the sub-array of elements between lo and hi (inclusive)
*       side effects:  sorts in place
*       assumes that lo < hi
*
*Entry:
*       uint4 *lo = pointer to low element to sort
*       uint4 *hi = pointer to high element to sort
*       unsigned width = width in bytes of each array element
*       int (*comp)() = pointer to function returning analog of strcmp for
*               strings, but supplied by user for comparing the array elements.
*               it accepts 2 pointers to elements and returns neg if 1<2, 0 if
*               1=2, pos if 1>2.
*
*Exit:
*       returns void
*
*Exceptions:
*
*******************************************************************************/

void shortsort ( uint4 *lo, uint4 *hi, unsigned char *data, uint4 minmatch )
{
    uint4 *p, *max, ml;

    /* Note: in assertions below, i and j are alway inside original bound of
       array to sort. */

    while (hi > lo) {
        /* A[i] <= A[j] for i <= j, j > hi */
        max = lo;
        for (p = lo+1; p <= hi; p++) {
            /* A[i] <= A[max] for lo <= i < p */
            if (qscompare(*p-minmatch, *max-minmatch, data, &ml) > 0) {
                max = p;
            }
            /* A[i] <= A[max] for lo <= i <= p */
        }

        /* A[i] <= A[max] for lo <= i <= hi */

        swap(max, hi)

        /* A[i] <= A[hi] for i <= hi, so A[i] <= A[j] for i <= j, j >= hi */

        hi--;

        /* A[i] <= A[j] for i <= j, j > hi, loop top condition established */
    }
    /* A[i] <= A[j] for i <= j, j > lo, which implies A[i] <= A[j] for i < j,
       so array is sorted */
}

/*
  rangecod.c     range encoding

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

  The input and output is done by the inbyte and outbyte macros
  defined in the .c file; change them as needed; the first parameter
  passed to them is a pointer to the rangecoder structure; extend that
  structure as needed (and don't forget to initialize the values in
  start_encoding resp. start_decoding). This distribution writes to
  stdout and reads from stdin.

  There are no global or static var's, so if the IO is thread save the
  whole rangecoder is.

  For error recovery the last 3 bytes written contain the total number
  of bytes written since starting the encoder. This can be used to
  locate the beginning of a block if you have only the end.

  There is a supplementary file called renorm95.c available at the
  website (www.compressconsult.com/rangecoder/) that changes the range
  coder to an arithmetic coder for speed comparisons.

  define RENORM95 if you want the old renormalisation. Requires renorm95.c
  Note that the old version does not write out the bytes since init.
  you should not define GLOBALRANGECODER then. This Flag is provided
  only for spped comparisons between both renormalizations, see my
  data compression conference article 1998 for details.
*/
/* #define RENORM95 */

/*
  define NOWARN if you do not expect more than 2^32 outstanding bytes 
  since I recommend restarting the coder in intervals of less than    
  2^23 symbols for error tolerance this is not expected
*/
#define NOWARN

/*
  define EXTRAFAST for increased speed; you loose compression and
  compatibility in exchange.
*/
#define EXTRAFAST

#include <stdio.h>		/* fprintf(), getchar(), putchar(), NULL */
// #include "port.h"
// #include "rangecod.h"

/* SIZE OF RANGE ENCODING CODE VALUES. */

#define CODE_BITS 32
#define Top_value ((code_value)1 << (CODE_BITS-1))


/* all IO is done by these macros - change them if you want to */
/* no checking is done - do it here if you want it             */
/* cod is a pointer to the used rangecoder                     */
#define outbyte(cod,x) putchar(x)
#define inbyte(cod)    getchar()


#ifdef RENORM95
// #include "renorm95.c"

#else
#define SHIFT_BITS (CODE_BITS - 9)
#define EXTRA_BITS ((CODE_BITS-2) % 8 + 1)
#define Bottom_value (Top_value >> 8)

#ifdef NOWARN
#ifdef GLOBALRANGECODER
char coderversion[]="rangecode 1.1c NOWARN GLOBAL (c) 1997-1999 Michael Schindler";
#else
char coderversion[]="rangecode 1.1c NOWARN (c) 1997-1999 Michael Schindler";
#endif
#else    /*NOWARN*/
#ifdef GLOBALRANGECODER
char coderversion[]="rangecode 1.1c GLOBAL (c) 1997-1999 Michael Schindler";
#else
char coderversion[]="rangecode 1.1c (c) 1997-1999 Michael Schindler";
#endif
#endif   /*NOWARN*/
#endif   /*RENORM95*/


#ifdef GLOBALRANGECODER
/* if this is defined we'll make a global variable rngc and    */
/* make RNGC use that var; we'll also omit unneeded parameters */
static rangecoder rngc;
#define RNGC (rngc)
#define M_outbyte(a) outbyte(&rngc,a)
#define M_inbyte inbyte(&rngc)
#define enc_normalize(rc) M_enc_normalize()
#define dec_normalize(rc) M_dec_normalize()
#else
#define RNGC (*rc)
#define M_outbyte(a) outbyte(rc,a)
#define M_inbyte inbyte(rc)
#endif


/* rc is the range coder to be used                            */
/* c is written as first byte in the datastream                */
/* one could do without c, but then you have an additional if  */
/* per outputbyte.                                             */
void start_encoding( rangecoder *rc, char c, int initlength )
{   RNGC.low = 0;                /* Full code range */
    RNGC.range = Top_value;
    RNGC.buffer = c;
    RNGC.help = 0;               /* No bytes to follow */
    RNGC.bytecount = initlength;
}


#ifndef RENORM95
/* I do the normalization before I need a defined state instead of */
/* after messing it up. This simplifies starting and ending.       */
static Inline void enc_normalize( rangecoder *rc )
{   while(RNGC.range <= Bottom_value)     /* do we need renormalisation?  */
    {   if (RNGC.low < (code_value)0xff<<SHIFT_BITS)  /* no carry possible --> output */
        {   M_outbyte(RNGC.buffer);
            for(; RNGC.help; RNGC.help--)
                M_outbyte(0xff);
            RNGC.buffer = (unsigned char)(RNGC.low >> SHIFT_BITS);
        } else if (RNGC.low & Top_value) /* carry now, no future carry */
        {   M_outbyte(RNGC.buffer+1);
            for(; RNGC.help; RNGC.help--)
                M_outbyte(0);
            RNGC.buffer = (unsigned char)(RNGC.low >> SHIFT_BITS);
        } else                           /* passes on a potential carry */
#ifdef NOWARN
            RNGC.help++;
#else
            if (RNGC.bytestofollow++ == 0xffffffffL)
            {   fprintf(stderr,"Too many bytes outstanding - File too large\n");
                exit(1);
            }
#endif
        RNGC.range <<= 8;
        RNGC.low = (RNGC.low<<8) & (Top_value-1);
        RNGC.bytecount++;
    }
}
#endif


/* Encode a symbol using frequencies                         */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
/* or (faster): tot_f = (code_value)1<<shift                             */
void encode_freq( rangecoder *rc, freq sy_f, freq lt_f, freq tot_f )
{	code_value r, tmp;
	enc_normalize( rc );
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

void encode_shift( rangecoder *rc, freq sy_f, freq lt_f, freq shift )
{	code_value r, tmp;
	enc_normalize( rc );
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


#ifndef RENORM95
/* Finish encoding                                           */
/* rc is the range coder to be used                          */
/* actually not that many bytes need to be output, but who   */
/* cares. I output them because decode will read them :)     */
/* the return value is the number of bytes written           */
uint4 done_encoding( rangecoder *rc )
{   uint tmp;
    enc_normalize(rc);     /* now we have a normalized state */
    RNGC.bytecount += 5;
    if ((RNGC.low & (Bottom_value-1)) < (RNGC.bytecount>>1))
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
/* returns the char from start_encoding or EOF               */
int start_decoding( rangecoder *rc )
{   int c = M_inbyte;
    if (c==EOF)
        return EOF;
    RNGC.buffer = M_inbyte;
    RNGC.low = RNGC.buffer >> (8-EXTRA_BITS);
    RNGC.range = (code_value)1 << EXTRA_BITS;
    return c;
}


static Inline void dec_normalize( rangecoder *rc )
{   while (RNGC.range <= Bottom_value)
    {   RNGC.low = (RNGC.low<<8) | ((RNGC.buffer<<EXTRA_BITS)&0xff);
        RNGC.buffer = M_inbyte;
        RNGC.low |= RNGC.buffer >> (8-EXTRA_BITS);
        RNGC.range <<= 8;
    }
}
#endif


/* Calculate culmulative frequency for next symbol. Does NO update!*/
/* rc is the range coder to be used                          */
/* tot_f is the total frequency                              */
/* or: totf is (code_value)1<<shift                                      */
/* returns the culmulative frequency                         */
freq decode_culfreq( rangecoder *rc, freq tot_f )
{   freq tmp;
    dec_normalize(rc);
    RNGC.help = RNGC.range/tot_f;
    tmp = RNGC.low/RNGC.help;
#ifdef EXTRAFAST
    return tmp;
#else
    return (tmp>=tot_f ? tot_f-1 : tmp);
#endif
}

freq decode_culshift( rangecoder *rc, freq shift )
{   freq tmp;
    dec_normalize(rc);
    RNGC.help = RNGC.range>>shift;
    tmp = RNGC.low/RNGC.help;
#ifdef EXTRAFAST
    return tmp;
#else
    return (tmp>>shift ? ((code_value)1<<shift)-1 : tmp);
#endif
}


/* Update decoding state                                     */
/* rc is the range coder to be used                          */
/* sy_f is the interval length (frequency of the symbol)     */
/* lt_f is the lower end (frequency sum of < symbols)        */
/* tot_f is the total interval length (total frequency sum)  */
void Inline decode_update( rangecoder *rc, freq sy_f, freq lt_f, freq tot_f)
{   code_value tmp;
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
unsigned char decode_byte(rangecoder *rc)
{   unsigned char tmp = decode_culshift(rc,8);
    decode_update( rc,1,tmp,(freq)1<<8);
    return tmp;
}

unsigned short decode_short(rangecoder *rc)
{   unsigned short tmp = decode_culshift(rc,16);
    decode_update( rc,1,tmp,(freq)1<<16);
    return tmp;
}


/* Finish decoding                                           */
/* rc is the range coder to be used                          */
void done_decoding( rangecoder *rc )
{   dec_normalize(rc);      /* normalize to use up all bytes */
}

// #include "port.h"

void reorder(unsigned char *in, unsigned char *out, uint4 length, uint recordsize)
{	uint4 i,j;
	for (i=0; i<recordsize; i++)
		for(j=i; j<length; j+=recordsize)
			*(out++) = in[j];
}

void unreorder(unsigned char *in, unsigned char *out, uint4 length, uint recordsize)
{	uint4 i,j;
	for (i=0; i<recordsize; i++)
		for(j=i; j<length; j+=recordsize)
			out[j] = *(in++);
}

/* b_i_t.c                                                                   */
/* this implements bit indexed trees for culmulative frequency storeage      */
/* described in                                                              */
/* Peter Fenwick: A New Data Structure for Cumulative Probability Tables     */
/* Technical Report 88, Dep. of Computer Science, University of Auckland, NZ */
/* I used it in Pascal in 1993? for random number generation                 */

// #include "sz_bit.h"
#include <stdio.h>
#include <stdlib.h>

/* returns the culmulative frequency <= the given symbol */
Inline freq getcf(symb s, cumtbl *tbl)
{ freq sum, *cf;
  sum = (cf=tbl->cf)[s+1] - tbl->f[s];
  s++;
  while (s &= s-1)
    sum += cf[s];
  return sum;
}

/* updates the given culmulative frequency */
Inline void updatecumonly(symb s, cumtbl *tbl, int delta)
{ freq *cf;
  symb size;
  tbl->totfreq += delta;
  s++;
  cf = tbl->cf;
  size = tbl->size;
  while (s<=size) {
     cf[s] += delta;
     s = (s | (s-1)) + 1;
  }
}

/* get symbol for this culmulative frequency */
Inline symb getsym(freq f, cumtbl *tbl)
{ symb s, m, x, size;
  freq *cf;
  m = tbl->mask;
  size = tbl->size;
  cf = tbl->cf;
  s = 0;
  do {
    if ((x=s|m) <= size && f >= cf[x]) {
      f -= cf[x];
      s = x;
    }
  } while (m >>= 1);
  return s;
}

#define RECALC(cond) {                   \
  symb i;                                \
  freq *cf;                              \
  cf = tbl->cf;                          \
  tbl->totfreq = 0;                      \
  for (i=1; i<=tbl->size; i<<=1) {       \
    symb j;                              \
    for (j=i; j<=tbl->size; j+= i<<1) {  \
      symb k;                            \
      if (cond)                          \
        cf[j] = 0;                       \
      else                               \
        tbl->totfreq += cf[j] = tbl->f[j-1];\
      for (k=i>>1; k; k>>=1)             \
        cf[j] += cf[j-k];                \
    } /* end for j */                    \
  } /* end for i */                      \
}

/* scales the culmulative frequency tables by 0.5 and keeps nonzero values */
void scalefreq(cumtbl *tbl)
{ freq *f, *endf;
  for (f=tbl->f, endf = f+tbl->size; f<endf; f++)
     *f = (*f + 1)>>1;
  RECALC(0);
}

/* scales the culmulative frequency tables by 0.5 and keeps nonzero values */
void scalefreqcond(cumtbl *tbl, uint *donotuse)
{ freq *f, *endf;
  for (f=tbl->f, endf = f+tbl->size; f<endf; f++)
     *f = (*f + 1)>>1;
  RECALC(donotuse[j-1]!=3);
}

/* allocates memory for the frequency table and initializes it */
int initfreq(cumtbl *tbl, symb tblsize, freq initvalue)
{ symb i;
  if ((tbl->f = (freq*)malloc(2*tblsize*sizeof(freq))) == NULL) return 1;
  tbl->cf = tbl->f + tblsize - 1;
  tbl->size = tblsize;
  tbl->mask = 1;
  while (tblsize>>=1)
     tbl->mask <<=1;
  for (i=0; i<tbl->size; i++)
     tbl->f[i] = initvalue;
  RECALC(0);
  return 0;
}

/* does the obvious thing */
void freefreq(cumtbl *tbl)
{ free(tbl->f);
}

/* szip.c                                                                   *
*                                                                           *
*  written by Michael Schindler michael@compressconsult.com                 *
*  1997,1998                                                                *
*  http://www.compressconsult.com/                                         */

static char vmayor=1, vminor=12;

#include <stdio.h>
#include <stdlib.h>
#ifndef unix
// #include <io.h>
#include <fcntl.h>
#endif
#include <string.h>
#include <ctype.h>
// #include "szip.h"
#include <sys/stat.h>

#define BLOCK_SIZE (1 << SIZE_SHIFT)
#define COMPRESSION_TYPE_SZIP 'S'

static void usage()
{   fprintf(stderr,"szip %d.%d (c)1997-2000 Michael Schindler, szip@compressconsult.com\n",
        vmayor, vminor);
    fprintf(stderr,"homepage: http://www.compressconsult.com/szip/\n");
    fprintf(stderr,"usage: szip [options] [inputfile [outputfile]]\n");
    fprintf(stderr,"option           meaning              default   range\n");
    fprintf(stderr,"-d               decompress\n");
    fprintf(stderr,"-b<blocksize>    blocksize in 100kB   -b1      1-41\n"); // default block size to minimum for ESP32-friendly decompression
    fprintf(stderr,"-o<order>        order of context     -o6       0, 3-255\n");
    fprintf(stderr,"-r<recordsize>   recordsize           -r1       1-127\n");
    fprintf(stderr,"-i               incremental          -i\n");
    fprintf(stderr,"-v<level>        verbositylevel       -v0       0-255\n");
    fprintf(stderr,"options may be combined into one, like -r3i\n");
    exit(1);
}

static int readnum(char **s, int min, int max)
{	int j=0;
	while (isdigit(**s))
	{	j=10*j+**s-'0';
		*s += 1;
	}
	if (j<min || j>max)
		usage();
	return j;
}

/* parameter values */
// uint4 blocksize=1703936;
uint4 blocksize = 32768; // 32 KB = 0x8000, ESP32-friendly default
uint order=6, verbosity=0, compress=1;
unsigned char recordsize=1;

static void no_szip()
{   fprintf(stderr, "probably not an szip file; could be szip version prior to 1.10\n");
    exit(1);
}

static void writeglobalheader(uint4 orig_size) 
{   /* Write Agon compression header prefix: "Cmp" and COMPRESSION_TYPE_SZIP */
    putchar('C');
    putchar('m');
    putchar('p');
    putchar(COMPRESSION_TYPE_SZIP);
    /* Write original file size (4 bytes, little-endian order) */
    putchar(orig_size & 0xFF);
    putchar((orig_size >> 8) & 0xFF);
    putchar((orig_size >> 16) & 0xFF);
    putchar((orig_size >> 24) & 0xFF);
    /* write SZIP magic SZ\012\004 and version numbers */
    putchar(0x53); // S
    putchar(0x5a); // Z
    putchar(0x0a); // \n
    putchar(0x04); // \004
    putchar(vmayor); /* version mayor of first version using the format */
    putchar(vminor); /* version minor of first version using the format */
}

static void readglobalheader()
{   /* Verify the Agon compression header prefix */
    if (getchar() != 'C') no_szip();
    if (getchar() != 'm') no_szip();
    if (getchar() != 'p') no_szip();
    if (getchar() != COMPRESSION_TYPE_SZIP) no_szip();
    /* Read the original file size (4 bytes, little-endian order).
       We could store this value if needed; for now we just read and ignore it. */
    uint4 orig_size = 0;
    orig_size |= (uint4)(unsigned char)getchar();
    orig_size |= (uint4)(unsigned char)getchar() << 8;
    orig_size |= (uint4)(unsigned char)getchar() << 16;
    orig_size |= (uint4)(unsigned char)getchar() << 24;

    /* Verify the SZIP magic SZ\012\004 and version numbers */
    int ch, vmay;
    ch = getchar();
    if (ch == EOF) return;
    if (ch == 0x42) {ungetc(ch, stdin); return;} /* maybe blockheader */
    if (ch != 0x53) no_szip();
    if (getchar() != 0x5a) no_szip();
    if (getchar() != 0x0a) no_szip();
    if (getchar() != 0x04) no_szip();
    vmay = getchar();
    if (vmay == EOF || vmay==0) no_szip();
    ch = getchar();
    if (ch == EOF) no_szip();
    if (vmay>vmayor || (vmay==vmayor && ch>vminor))
    {   fprintf(stderr, "This file is szip version %d.%d, this program is %d.%d.\n Please update\n",
        vmay, ch, vmayor, vminor);
        exit(1);
    }
    if (vmay==1 && ch==10)
    {   fprintf(stderr, "This file is szip version 1.10ALPHAi");
        fprintf(stderr, "A decoder is available at the website http://www.compressconsult.com");
        exit(1);
    }
}


static void writeuint3(uint4 x)
{   putchar((char)((x>>16)&0xff));
    putchar((char)((x>>8)&0xff));
    putchar((char)(x&0xff));
}


static uint4 readuint3()
{   uint4 x;
    x = getchar();
    x = x<<8 | getchar();
    x = x<<8 | getchar();
    return x;
}


static uint writeblockdir(uint4 buflen)
{   /* write magic */
    putchar(0x42);
    putchar(0x48);
    writeuint3(buflen);
    putchar(0);   /* FIXME: empty filename to indicate end of dir */
    return 6;
}


static uint readblockdir(uint4 *buflen)
{   int ch;
    ch = getchar();
    if (ch == EOF) {*buflen = 0; return 0;}
    if (ch == 0x53)
    {   ungetc(ch, stdin);
        readglobalheader();
        ch=getchar();
        if (ch == EOF) {*buflen = 0; return 0;}
    }
    if (ch != 0x42) no_szip();
    if (getchar() != 0x48) no_szip();
    *buflen = readuint3();
    if (getchar() != 0) no_szip();  /* FIXME: read until empty filename */
    return 6;
} 


static void writestorblock(uint dirsize, uint4 buflen, unsigned char *buffer)
{   unsigned char *end;
    if (verbosity&1) fprintf( stderr, "Storing %d bytes ...", buflen);
    putchar(0); /* 0 means stored block */
    end = buffer + buflen;
    while (buffer<end)
    {   putchar(*buffer);
        buffer++;
    }
    writeuint3(dirsize+4+buflen);
}


static void readstorblock(uint dirsize, uint4 buflen, unsigned char *buffer)
{   if (verbosity&1) fprintf( stderr, "Reading %d bytes ...", buflen);
    if (fread(buffer,1,buflen,stdin) != buflen)
    {   fprintf(stderr,"Error reading input\n"); exit(1);}
    if (fwrite(buffer,1,buflen,stdout) != buflen)
    {   fprintf(stderr,"Error writing output\n"); exit(1);}
    if (readuint3() != dirsize+3+buflen) no_szip();
}

   
static void writeszipblock(uint dirsize, uint4 buflen, unsigned char *buffer)
{   uint4 indexlast;
#ifndef MODELGLOBAL
    sz_model m;
#endif
    if (verbosity&1) fprintf( stderr, "Processing %d bytes ...", buflen);
    putchar(1); /* 1 means szip block */
    if ((recordsize&0x7f) != 1)
    {	unsigned char *tmp;
		tmp = (unsigned char*) malloc(buflen+order);
		if (tmp==NULL)
		{	fprintf(stderr, "memory allocation error\n");
			exit(1);
		}
		reorder(buffer,tmp,buflen,recordsize&0x7f);
        memcpy(buffer,tmp,buflen);
		free(tmp);
	}

    if (recordsize &0x80)
	{	unsigned char tmp = *buffer;
        uint4 i;
		for (i=1; i<buflen; i++)
		{	unsigned char tmp1 = buffer[i];
			buffer[i] = (0x100 + tmp1 - tmp) & 0xff;
			tmp = tmp1;
		}
	}

    if (order==4)
		sz_srt_o4(buffer,buflen,&indexlast);
	else if (order==0)
		sz_srt_BW(buffer,buflen,&indexlast);
	else
		sz_srt(buffer,buflen,&indexlast,order);

    if (verbosity&1) fprintf(stderr," coding ...");

    writeuint3(indexlast);
    putchar((char)(order&0xff));

    initmodel(&m, dirsize+5, &recordsize);
    /* FIXME: write recordsize with putchar with planned output */

  { unsigned char *end;
    end = buffer+buflen;
    *end = ~*(end-1); /* to make sure we end a run at end */
   {unsigned char ch, *begin;
    begin = buffer;
    ch = *(buffer++);
    while (*buffer==ch)
       buffer++;
    sz_encode(&m, ch, (uint4)(buffer-begin));
   }
    fixafterfirst(&m);
    while (buffer<end)
    {   unsigned char ch, *begin;
        begin = buffer;
        ch = *(buffer++);
        while (*buffer==ch)
            buffer++;
        sz_encode(&m, ch, (uint4)(buffer-begin));
    }
  }

    // #ifndef MODELGLOBAL
    //     FILE *model_file = fopen("0szip_model.bin", "wb");
    //     fwrite(&m, sizeof(sz_model), 1, model_file);
    //     fclose(model_file);
    // #else
    //     fwrite(m, sizeof(sz_model), 1, model_file);
    // #endif // MODELGLOBAL

    deletemodel(&m);
}


static void readszipblock(uint dirsize, uint4 buflen, unsigned char *buffer)
{   unsigned char *tmp;
    uint4 indexlast, charcount[256], bytesleft;
#ifndef MODELGLOBAL
    sz_model m;
#endif
    if (verbosity&1) fprintf( stderr, "Decoding %d bytes ", buflen);
    indexlast = readuint3();
    order = getchar();

	memset(charcount, 0, 256*sizeof(uint4));
    initmodel(&m, -1, &recordsize);

    if (verbosity&1)
    {   if (order != 6)
            fprintf( stderr, "-o%d ",order);
        if ((recordsize & 0x7f) != 1)
            fprintf( stderr, "-r%d ",recordsize&0x7f);
        if (recordsize & 0x80)
            fprintf( stderr, "-i ");
        fprintf( stderr, "...");
    }

    tmp = buffer;
    bytesleft = buflen;
    {   uint4 runlength;
        uint ch;
        sz_decode(&m, &ch, &runlength);
        if (runlength>bytesleft)
        {	fprintf(stderr, "input file corrupt");
			exit(1);
		}
        bytesleft -= runlength;
        charcount[ch] += runlength;
        while (runlength)
        {   *(tmp++) = ch;
            runlength--;
        }
    }
    fixafterfirst(&m);
    while (bytesleft)
    {   uint4 runlength;
        uint ch;
        sz_decode(&m, &ch, &runlength);
        if (runlength>bytesleft)
        {	fprintf(stderr, "input file corrupt");
			exit(1);
		}
        bytesleft -= runlength;
        charcount[ch] += runlength;
        while (runlength)
        {   *(tmp++) = ch;
            runlength--;
        }
    }
    deletemodel(&m);

    if (verbosity&1) fprintf( stderr, " processing ...");

	if (recordsize == 1)
	{	if (order==0)
			sz_unsrt_BW(buffer, NULL, buflen, indexlast, charcount);
		else
			sz_unsrt(buffer, NULL, buflen, indexlast, charcount, order);
//fwrite(buffer,1,buflen,stdout);
    }
	else
	{	tmp = (unsigned char*) malloc(buflen);
		if (tmp==NULL)
		{	fprintf(stderr, "memory allocation failure");
			exit(1);
		}
		if (order==0)
			sz_unsrt_BW(buffer, tmp, buflen, indexlast, charcount);
		else
			sz_unsrt(buffer, tmp, buflen, indexlast, charcount, order);
		if (recordsize & 0x80)
		{	uint4 i;
            unsigned char c = *tmp;
			for (i=1; i<buflen; i++)
			{	c = (c+tmp[i])&0xff;
				tmp[i] = c;
			}
		}
		unreorder(tmp,buffer,buflen,recordsize&0x7f);
		free(tmp);

        bytesleft = fwrite(buffer,1,buflen,stdout);
        if (bytesleft != buflen)
		{	fprintf(stderr, "error writing output");
			exit(1);
		}
    }
}


static void compressit()
{   unsigned char *inoutbuffer;

    inoutbuffer = (unsigned char*) malloc(blocksize+order+1);
	if (inoutbuffer==NULL)
	{	fprintf(stderr, "memory allocation error\n");
		exit(1);
	}

    /* Attempt to get the original file size from stdin */
    uint4 orig_size = 0;
    struct stat st;
    if (fstat(fileno(stdin), &st) == 0) {
        orig_size = (uint4) st.st_size;
        /* If stdin is a regular file, rewind to the beginning */
        if (S_ISREG(st.st_mode)) {
            rewind(stdin);
        }
    } else {
        fprintf(stderr, "Warning: unable to determine file size; using 0\n");
    }

    writeglobalheader(orig_size);

    while (1)
    {   uint4 buflen;
        uint i;
        buflen = fread( (char *)inoutbuffer, 1, (size_t)blocksize, stdin);
        if (buflen == 0) break;

        i = writeblockdir(buflen);

        if (buflen<=order || buflen<=5)
            writestorblock(i, buflen, inoutbuffer);
        else
            writeszipblock(i, buflen, inoutbuffer);

		if (verbosity&1) fprintf(stderr," done\n");
	}
    free(inoutbuffer);
}


static void decompressit()
{   unsigned char *inoutbuffer=NULL;

    blocksize = 0;
    readglobalheader();

    while (1)
    {   uint4 blocklen;
        uint dirsize;
        int ch;
        dirsize = readblockdir(&blocklen);
        if (dirsize==0) break;
        if (blocklen>blocksize)
        {   if (inoutbuffer != NULL)
                free(inoutbuffer);
            inoutbuffer = (unsigned char *) malloc(blocklen);
            blocksize = blocklen;
        	if (inoutbuffer==NULL)
        	{	fprintf(stderr, "memory allocation error\n");
        		exit(1);
	        }
        }
        ch = getchar();
        if (ch==0)
            readstorblock(dirsize+1, blocklen, inoutbuffer);
        else if (ch==1)
            readszipblock(dirsize+1, blocklen, inoutbuffer);
        else
            no_szip();
		if (verbosity&1) fprintf(stderr," done\n");
	}
    free(inoutbuffer);
}


int main( int argc, char *argv[] )
{	char *infilename=NULL, *outfilename=NULL;
    uint i;

    for (i=1; i<(unsigned)argc; i++)
	{	char *s=argv[i];
	    if (*s == '-')
		{	s++;
			while (*s)
				switch (*(s++))
				{	
                    case 'o': {
                        order = readnum(&s, 0, 255);
                        if (order == 1 || order == 2) {
                            usage();
                        }
                        break;
                    }                    
					case 'r': {recordsize = (recordsize & 0x80) | 
								  readnum(&s,1,255); break;}
					// case 'b': {blocksize = (100000*readnum(&s,1,41)+0x7fff) & 0x7fff8000L; break;}
                    case 'b': { // modification for ESP32-friendly block size
                        uint custom_size = readnum(&s, 1, 41) * 100000; // User-specified size in 100 KB units
                        if (custom_size < 32768) { // Ensure blocksize never goes below 32 KB
                            custom_size = 32768;
                        }
                        blocksize = (custom_size + 0x7fff) & 0x7FFF8000L; // Align to 32 KB boundary
                        break;
                    } // end modification for ESP32-friendly block size
					case 'i': {recordsize |= 0x80; break;}
                    case 'v': {verbosity = readnum(&s,0,255); break;}
                    case 'd': {compress = 0; break;}
					default: usage();
				}
		} else if (infilename == NULL)
			infilename = s;
		else if (outfilename == NULL)
			outfilename = s;
		else
			usage();
	}

	if (verbosity) fprintf( stderr, "szip Version %d.%d on ", vmayor, vminor);

    if (infilename == NULL) {
        if (verbosity) fprintf(stderr, "stdin");
    } else {
        if (!freopen(infilename, "rb", stdin)) {
            fprintf(stderr, "Error opening input file: %s\n", infilename);
            exit(1);
        }
        if (verbosity) fprintf(stderr, "%s", infilename);
    }
    
    if (outfilename == NULL) {
        if (verbosity) fprintf(stderr, " to stdout\n");
    } else {
        if (!freopen(outfilename, "wb", stdout)) {
            fprintf(stderr, "Error opening output file: %s\n", outfilename);
            exit(1);
        }
        if (verbosity) fprintf(stderr, " to %s\n", outfilename);
    }    

#ifndef unix
    setmode( fileno( stdin ), O_BINARY );
    setmode( fileno( stdout ), O_BINARY );
#endif

    if (compress) {
        compressit();
    } else {
        decompressit();
    }

    return 0;
}

/* sz_mod4.c   (c) Michael Schindler, 1998
*
* This file is a probability model for blocksorted files.
* It uses the rangecoder (rangecod.c) as entropy coder and some
* other modules (qsmodel, bitmodel) to maintain statistics information.
* You have to call initmodel() to initialize the model and after
* encoding the first run you need to call fixafterfirst.
* closeszmodel finishes output.
* you may use the rangecoder model->rc for other purposes in between,
* provided that you do the same at decoding.
*
* This model always encodes <submodel><symbol><repeatcount> triples,
* where submodel is one of 3 possible models to encode a symbol.
*
* submodel 0 is a cache of the last 31 symbols seen (with repetition
* allowed), with the most recent symbol excluded (except after
* initialisation). The probabilities for symbols in cache are
* derived from their nuber of occurance and the runlengths.
*
* submodel 1 is a move-to-front (MTF) containing the MTFSIZE most
* recent symbols no longer on submodel 0. Probabilities are based
* on MTF rank here.
*
* submodel 2 contains symbols neither in submodel 0 or submodel 1.
*
* Symbols are moved between models lazily; an update is done only
* when needed.
*
* The probabilities for the submodel are derived from the most recent
* history; each submodel has a frequency of:
* 1 + #occurences in last 31 symbols + 5*#occurances in last 6 symbols,
* giving a total count of 64.
*
* The runlength code is an array of 5 quasistatic models, each
* containing 7 symbols. those symbols mean:
*  symbol   # extra bits     runlength
*    0         0             1
*    1         0             2
*    2         0             3
*    3         0             4
*    4         2             5+extra (5..8)
*    5         3             9+extra (9..16)
*    6         5             extra>16 ? extra : extra+5 bit follow,
*                               these bits preceded by 1 give the length
*
* the 5 runlength models are used for:
* 0:new symbols;  1:rl=1;  2:rl=2,3;  3: rl=4-8;  4: rl=9+
* model 1 is also used if the symbol was not seen in the last 6 symbols.
*/

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>   /* exit() */
// #include "sz_mod4.h"

#define RLSHIFT 10
#define MTFSHIFT 10

#define FULLFLAG (MOD.cache-1)
#define MTFFLAG (MOD.cache-2)

#ifdef MODELGLOBAL
sz_model mod;
#define dumpcache(m) M_dumpcache()
#define decodewhat(m) M_decodewhat()
#define finishupdate(m,a) M_finishupdate(a)
#define addtomtf(m,a) M_addtomtf(a)
#define encodeother(m,a) M_encodeother(a)
#define readrunlength(m) M_readrun()
#define activatenext(m,a) M_activatenext(a)
#define MOD mod
#else
#define MOD (*m)
#endif

#if 0
static void dumpcache(sz_model *m)
{ uint i, last, bug=0;
  int sum;
  if (MOD.cachetotf>7*MAXCACHESIZE)
  { fprintf(stderr, "bug: sum too large\n");
    bug = 1;
  }
  last = MOD.cachefirst&(CACHESIZE-1);
  sum = MOD.cachetotf;
  for(i=0; i<MOD.cachesize; i++)
    sum -= MOD.cache[(CACHESIZE+last-i)&(CACHESIZE-1)].sy_f;
  if (sum!=0)
    { fprintf(stderr, "bug: sum=%4d !!!\n",sum);
      bug = 1;
    }
  for(i=0; i<MOD.cachesize; i++)
    if(MOD.lastseen[MOD.cache[(CACHESIZE+last-i)&(CACHESIZE-1)].symbol]>CACHESIZE)
    { fprintf(stderr, "bug: symbol flagged as not in cache!!!\n");
      bug = 1;
    }
 
  if (!bug)
    return;
  fprintf(stderr,"size:%2d last:%2d totf:%4d\nsymbol",MOD.cachesize, last, MOD.cachetotf);
  for(i=0; i<MOD.cachesize; i++)
    fprintf(stderr,"%4d",MOD.cache[(CACHESIZE+last-i)&(CACHESIZE-1)].symbol);
  fprintf(stderr,"\nrunlen");
  for(i=0; i<MOD.cachesize; i++)
    fprintf(stderr,"%4d",MOD.cache[(CACHESIZE+last-i)&(CACHESIZE-1)].rl);
  fprintf(stderr,"\nsy_f  ");
  for(i=0; i<MOD.cachesize; i++)
    fprintf(stderr,"%4d",MOD.cache[(CACHESIZE+last-i)&(CACHESIZE-1)].sy_f);
  fprintf(stderr,"\nindex ");
  for(i=0; i<MOD.cachesize; i++)
    fprintf(stderr,"%4d",(CACHESIZE+last-i)&(CACHESIZE-1));
  fprintf(stderr,"\nl_seen");
  for(i=0; i<MOD.cachesize; i++)
    fprintf(stderr,"%4d",MOD.lastseen[MOD.cache[(CACHESIZE+last-i)&(CACHESIZE-1)].symbol]);
  fprintf(stderr,"\n");
}


static void dumpmtf(sz_model *m)
{   int n, i, bug=0, inmtf[256];
    for(i=0; i<256; i++)
    {   if(((m->full.f[i]&0x8000)==0) != (m->lastseen[i]==FULLFLAG))
        {   fprintf(stderr,"full bug: flag and inactive don't match for %d Flag:%d  f:%d\n",
            i, m->lastseen[i], m->full.f[i]);
            bug=1;
        }
        inmtf[i] = 0;
    }
            
    if (m->mtfsizeact > m->mtfsize)
    {   fprintf(stderr,"mtf bug: actsize (%d) larger than mtfsize (%d)\n",
            m->mtfsizeact, m->mtfsize);
        bug=1;
    }
    if (m->full.totalfreq < 0)
    {   fprintf(stderr,"full bug: total frequency (%d) wrong\n", m->full.totalfreq);
        bug=1;
    }
    i = m->mtffirst;
    for (n=0; n<m->mtfsizeact; n++)
    {   int sym=m->mtfhist[i].sym;
        if (i>MTFHISTSIZE)
        {   fprintf(stderr,"mtf bug: invalid next (%d)\n", n);
            bug=1;
        }
        if (m->lastseen[sym]<CACHESIZE)
        {   fprintf(stderr,"mtf bug: active mtf symbol (%d,%d) in cache\n", sym, n);
            bug=1;
        }
        if (m->lastseen[sym] == FULLFLAG) 
        {   fprintf(stderr,"mtf bug: active mtf symbol (%d,%d) in full\n", sym, n);
            bug=1;
        }
        if (inmtf[m->mtfhist[i].sym] != 0) 
        {   fprintf(stderr,"mtf bug: active mtf symbol (%d,%d) doubled\n", sym, n);
            bug=1;
        }
        inmtf[m->mtfhist[i].sym]++;

        i=m->mtfhist[i].next;
    }
    for (; n<m->mtfsize; n++)
    {   int sym=m->mtfhist[i].sym;
        if (i>MTFHISTSIZE)
        {   fprintf(stderr,"mtf bug: invalid next (%d)\n", n);
            bug=1;
        }
        i=m->mtfhist[i].next;
    }
    i=m->mtffirst;
    if (bug)
    {   fprintf(stderr,"mtfsize: %3d  active: %3d\n", m->mtfsize, m->mtfsizeact);
        for (n=0; n<m->mtfsize; n++)
        {   int sym=m->mtfhist[i].sym;
            fprintf(stderr,"n: %3d  i: %3d  sym: %3d  next:%3d  active: %1d\n",
                n, i, m->mtfhist[i].sym, m->mtfhist[i].next, n<m->mtfsizeact);
            i=m->mtfhist[i].next;
        }
        n=i;
    }

}


/* decode what model was used */
static Inline int decodewhat(sz_model *m)
{   int sy_f, lt_f, mod;
    mod = qsgetsym( &(MOD.what), decode_culshift( &(MOD.ac), WHATSHIFT));
    qsgetfreq( &(MOD.what), mod, &sy_f, &lt_f );
    decode_update_shift(&(MOD.ac), sy_f, lt_f, WHATSHIFT);
    qsupdate( &(MOD.what), mod);
    return mod;
}
#endif


/* add a new symbol to MTF list */
static void addtomtf(sz_model *m, uint sym)
{   uint i = (MOD.mtffirst+1) & (MTFHISTSIZE-1);
    if (MOD.mtfhist[i].next == 0xffff)      /* an empty place */
    {   MOD.mtfsize++;
        MOD.mtfsizeact++;
    }
    else if (MOD.mtfsizeact==MOD.mtfsize)   /* occupied by active symbol */
    {   MOD.lastseen[MOD.mtfhist[i].sym] = FULLFLAG;
        bitreactivate(&(MOD.full),MOD.mtfhist[i].sym);
    }
    else                                    /* occupied by inactive symbol*/
        MOD.mtfsizeact++;
    MOD.mtfhist[i].next = MOD.mtffirst;
    MOD.mtfhist[i].sym = sym;
    MOD.mtffirst = i;
    MOD.lastseen[sym] = MTFFLAG;
}


/* finish updating the model
* this assumes that the following has been done properly:
* probability updating of RLE models/MTF models/full model
* m.newest points to the free entry
* m.newest->sy_f , weight and what are properly filled
* the symbol has been disabled in the old place (removed from MTF,
* set inactive in full or sy_f cleared for cache
* this will do the following: adjust lastseen.
* adjust m.cachetotf
* adjust m.whatmod
* advance m.lastnew
* modify lastseen
* free the next available element in cache */
static void finishupdate(sz_model *m, uint symbol)
{   cacheptr tmp;
    tmp = MOD.newest; /* make tmp point to new element */
    MOD.lastseen[symbol] = tmp;
    tmp->symbol = symbol;
    MOD.cachetotf += tmp->weight;
    tmp = tmp->next; /* make tmp point to the to be cleared element */
    MOD.whatmod[tmp->what] --;
    if (!tmp->sy_f)
    	(MOD.lastseen[tmp->symbol])->sy_f --;
	else /* last instance, move to MTF */
        addtomtf(m,tmp->symbol);
    tmp = MOD.lastnew; /* make tmp point to adjustment place */
    MOD.whatmod[tmp->what] -= 5;
    MOD.cachetotf -= tmp->weight;
    MOD.lastseen[tmp->symbol]->sy_f -= tmp->weight-1;
    tmp->weight = 1;
    MOD.lastnew = tmp->next;
}
        

/* encode non-cache symbols */
static unsigned char encodeother(sz_model *m, uint sym)
{   uint i, n, last;
    i = MOD.mtffirst;
    last = i;
    if (MOD.mtfsizeact >= MTFSIZE) /* we have enough active symbols */
    {   for (n=0; n<MTFSIZE; n++)
        {   if (MOD.mtfhist[i].sym == sym)
                goto found;
            last = i;
            i = MOD.mtfhist[i].next;
        }
        /* we didn't find it, so move all remaining active symbols to inactive */
        for (; n<MOD.mtfsizeact; n++)
        {   MOD.lastseen[MOD.mtfhist[i].sym] = FULLFLAG;
            bitreactivate(&(MOD.full),MOD.mtfhist[i].sym);
            i = MOD.mtfhist[i].next;
        }
        MOD.mtfsizeact = MTFSIZE;
    }
    else
    {   for (n=0; n<MOD.mtfsizeact; n++)
        {   if (MOD.mtfhist[i].sym == sym)
                goto found;
            last = i;
            i = MOD.mtfhist[i].next;
        }
        /* we didn't find it, so try to make more active */
        MOD.mtfsizeact = MOD.mtfsize>MTFSIZE ? MTFSIZE : MOD.mtfsize;
        while (n<MOD.mtfsizeact)
        {   if (MOD.lastseen[MOD.mtfhist[i].sym]==FULLFLAG)
            {   MOD.lastseen[MOD.mtfhist[i].sym] = MTFFLAG;
                bitdeactivate(&(MOD.full),MOD.mtfhist[i].sym);
                if (MOD.mtfhist[i].sym == sym)
                {   MOD.mtfsizeact = n+1;
                    goto found;
                }
                last = i;
                i = MOD.mtfhist[i].next;
                n++;
            }
            else /* symbol in cache or active MTF; remove from list */
            {   int next = MOD.mtfhist[i].next;
                if(n>0) MOD.mtfhist[last].next = next;
                else MOD.mtffirst = next;
                MOD.mtfhist[i].next = 0xffff;
                i = next;
                MOD.mtfsize--;
                if (MOD.mtfsizeact > MOD.mtfsize)
                    MOD.mtfsizeact = MOD.mtfsize;
            }
        }
    }
    /* we didn't find it, so use full model */
    encode_shift(&(MOD.ac), MOD.whatmod[2], MOD.whatmod[0]+MOD.whatmod[1], 6);
    MOD.whatmod[2]+=6;
  { int sy_f, lt_f;
    bitgetfreq(&(MOD.full),sym,&sy_f, &lt_f);
    encode_freq(&(MOD.ac),sy_f,lt_f,bittotf(&(MOD.full)));
    bitupdate_ex(&(MOD.full),sym);
    return 2;
  }
found: /* we found it in MTF, so encode it and remove it */
    encode_shift(&(MOD.ac), MOD.whatmod[1], MOD.whatmod[0], 6);
    MOD.whatmod[1]+=6;
  { int sy_f, lt_f;
    qsgetfreq(&(MOD.mtfmod), n, &sy_f, &lt_f);
    encode_shift(&(MOD.ac), sy_f, lt_f, MTFSHIFT);
    qsupdate(&(MOD.mtfmod), n);
  }
    if (n==0)
        MOD.mtffirst = MOD.mtfhist[i].next;
    else
        MOD.mtfhist[last].next= MOD.mtfhist[i].next;
    MOD.mtfhist[i].next = 0xffff;
    MOD.mtfsize--;
    MOD.mtfsizeact--;
    return 1;
}

static unsigned char readrun(qsmodel *rlmod, uint4 *n)
{   int sy_f, lt_f, rl;
    rl = qsgetsym( rlmod, decode_culshift( &(MOD.ac), RLSHIFT));
    qsgetfreq( rlmod, rl, &sy_f, &lt_f );
    decode_update_shift(&(MOD.ac), sy_f, lt_f, RLSHIFT);
    qsupdate( rlmod, rl);
    if (rl<=3)   /* no extra bits */
    {   rl++;
        *n = rl;
        return (1 + (rl>>1));
    }
    if (rl==4)  /* two extra bits */
    {   rl = decode_culshift( &(MOD.ac), 2);
        decode_update_shift(&(MOD.ac), 1, rl, 2);
        *n = rl + 5;
        return 3;
    }
    if (rl==5)  /* three extra bits */
    {   rl = decode_culshift( &(MOD.ac), 3);
        decode_update_shift(&(MOD.ac), 1, rl, 3);
        *n = rl + 9;
        return 4;
    }
    /* five extra bits */
    rl = decode_culshift( &(MOD.ac), 5);
    decode_update_shift(&(MOD.ac), 1, rl, 5);
    if (rl>16)
        *n = rl;
    else
    {   uint4 bits;
        rl += 5;
        bits = decode_culshift( &(MOD.ac), rl);
        decode_update_shift(&(MOD.ac), 1, bits, rl);
        *n = bits + ((uint4)1 << rl);
    }
    return 4;
}


/* writes out the runlength */
static unsigned char writerun(qsmodel *rlmod, uint4 n)
{   int sy_f, lt_f;
	if (n<=4)       /* no extra bits */
    {   qsgetfreq( rlmod, n-1, &sy_f, &lt_f );
        encode_shift( &(MOD.ac), (freq)sy_f, (freq)lt_f, RLSHIFT);
        qsupdate( rlmod, n-1);
        return (1 + (n>>1));
    }
    if (n<=8)       /* two extra bits */
    {   qsgetfreq( rlmod, 4, &sy_f, &lt_f );
        encode_shift( &(MOD.ac), (freq)sy_f, (freq)lt_f, RLSHIFT);
        encode_shift( &(MOD.ac), (freq)1, (freq)(n-5), 2);
        qsupdate( rlmod, 4);
	    return 3;
    }
    if (n<=16)      /* three extra bits */
    {   qsgetfreq( rlmod, 5, &sy_f, &lt_f );
        encode_shift( &(MOD.ac), (freq)sy_f, (freq)lt_f, RLSHIFT);
        encode_shift( &(MOD.ac), (freq)1, (freq)(n-9), 3);
        qsupdate( rlmod, 5);
	    return 4;
    }
	qsgetfreq( rlmod, 6, &sy_f, &lt_f );
	encode_shift( &(MOD.ac), (freq)sy_f, (freq)lt_f, RLSHIFT);
	if (n < 32) /* five extra bits; n must be >16 here */
		encode_shift( &(MOD.ac), (freq)1, (freq)n, 5);
	else        /* #extra bits-5, 5 to 21 extra bits without leading 1 */
	{   uint i;
		for (i=5; n>>i > 1; i++)
            /* void */;
        encode_shift( &(MOD.ac), (freq)1, (freq)(i-5), 5);
	    encode_shift( &(MOD.ac), (freq)1, (freq)(n-((uint4)1<<i)), i);
	}
	qsupdate( rlmod, 6);
	return 4;
}

void sz_encode(sz_model *m, uint symbol, uint4 runlength)
{   cacheptr tmp;

    /* now encode what is the next symbol, first what model to use */
    /* then within the model */
    if ((tmp=MOD.lastseen[symbol]) >= MOD.cache) /* symbol in cache */
    {   uint lt_f;
        cacheptr old;
        encode_shift(&(MOD.ac), MOD.whatmod[0], 0, 6);
        MOD.whatmod[0]+=6;
        old = tmp;
        lt_f = 0;
        tmp = tmp->next;
        while (tmp != MOD.newest)
        {   lt_f += tmp->sy_f;
            tmp = tmp->next;
        }
        encode_freq(&(MOD.ac), old->sy_f, lt_f, MOD.cachetotf - tmp->sy_f);
        tmp = tmp->next;
        tmp->what = 0;
        tmp->weight = writerun(MOD.rlemod + old->weight, runlength);
        tmp->sy_f = tmp->weight + old->sy_f;
        old->sy_f = 0;
        MOD.newest = tmp;
    }
    else
    {   tmp = MOD.newest->next;
        tmp->what = encodeother(m,symbol);
        tmp->weight = writerun(MOD.rlemod, runlength);
        tmp->sy_f = tmp->weight;
        MOD.newest = tmp;
    }
#ifdef MODELGLOBAL
    finishupdate(M,symbol);
#else
    finishupdate(m,symbol);
#endif
}


static int activatenext(sz_model *m, uint *next)
{   while (MOD.mtfsize>MOD.mtfsizeact)
    {   mtfentry *tmp;
        tmp = MOD.mtfhist + *next;
        if (MOD.lastseen[tmp->sym]==FULLFLAG)
        {   bitdeactivate(&(MOD.full),tmp->sym);
            MOD.lastseen[tmp->sym] = MTFFLAG;
            MOD.mtfsizeact++;
            return 1;
        }
        *next = tmp->next;
        tmp->next = 0xffff;
        MOD.mtfsize--;
    }
    return 0;
}


void sz_decode(sz_model *m, uint *symbol, uint4 *runlength)
{   uint sym;

    /* first decode what model was used in encoding */
    sym = decode_culshift( &(MOD.ac), 6);
    if (sym < MOD.whatmod[0])  /* cache */
    {   uint lt_f, tot_f;
        cacheptr tmp;
        decode_update_shift(&(MOD.ac), MOD.whatmod[0], 0, 6);
        MOD.whatmod[0] += 6;
        tmp = MOD.newest;
        tot_f = MOD.cachetotf - tmp->sy_f;
        sym = decode_culfreq( &(MOD.ac), tot_f);
        tmp = tmp->prev;
        lt_f = tmp->sy_f;
        while (lt_f <= sym)
        {   tmp = tmp->prev;
            lt_f += tmp->sy_f;
        }
        decode_update(&(MOD.ac), tmp->sy_f, lt_f-tmp->sy_f, tot_f);
      { cacheptr free = MOD.newest->next;
        MOD.newest = free;
        free->what = 0;
        free->weight = readrun(MOD.rlemod + tmp->weight, runlength);
        free->sy_f = free->weight + tmp->sy_f;
      }
        tmp->sy_f = 0;
        *symbol = tmp->symbol;
    }
    else if (sym < MOD.whatmod[0]+MOD.whatmod[1])  /* MTF */
    {   mtfentry *pred;
        int sy_f, lt_f;
        decode_update_shift(&(MOD.ac), MOD.whatmod[1], MOD.whatmod[0], 6);
        MOD.whatmod[1] += 6;
        sym = qsgetsym( &(MOD.mtfmod), decode_culshift( &(MOD.ac), MTFSHIFT));
        qsgetfreq( &(MOD.mtfmod), sym, &sy_f, &lt_f );
        decode_update_shift(&(MOD.ac), sy_f, lt_f, MTFSHIFT);
        qsupdate( &(MOD.mtfmod), sym);
        if (MOD.mtfsizeact == 0)
            activatenext(&MOD,&(MOD.mtffirst));

        pred = MOD.mtfhist + MOD.mtffirst;
        if (sym==0)    /* the first entry */
        {   if(MOD.mtfsizeact==0)
                activatenext(&MOD,&(MOD.mtffirst));
            pred = MOD.mtfhist + MOD.mtffirst;
            sym = pred->sym;
            MOD.mtffirst = pred->next;
            pred->next = 0xffff;
        }
        else
        {   uint n;
            mtfentry *target;
            if (sym < MOD.mtfsizeact) /* active list is large enough */
                for (n=sym-1; n; n--) /* skip unneeded part of MTF */
                    pred = MOD.mtfhist + pred->next;
            else
            {   for (n=MOD.mtfsizeact-1; n; n--) /* skip active part of MTF */
                    pred = MOD.mtfhist + pred->next;
                while (MOD.mtfsizeact<sym)
                {   activatenext(&MOD,&(pred->next));
                    pred = MOD.mtfhist + pred->next;
                }
                activatenext(&MOD,&(pred->next));
            }
            target = MOD.mtfhist + pred->next;
            sym = target->sym;
            pred->next = target->next;
            target->next = 0xffff;
        }
        MOD.mtfsizeact--;
        MOD.mtfsize--;
      { cacheptr free = MOD.newest->next;
        MOD.newest = free;
        free->what = 1;
        free->weight = readrun(MOD.rlemod, runlength);
        free->sy_f = free->weight;
      }
        *symbol = sym;
    }
    else /* full model */
    {   int sy_f, lt_f;
        decode_update_shift(&(MOD.ac), MOD.whatmod[2], MOD.whatmod[0]+MOD.whatmod[1], 6);
        MOD.whatmod[2] += 6;
        /* first adjust the size of the MTF */
        if (MOD.mtfsizeact>MTFSIZE) /* active MTF too big */
        {   uint n, i;
            i = MOD.mtffirst;
            for (n=0; n<MTFSIZE; n++) /* skip active part of MTF */
                i = MOD.mtfhist[i].next;
            while (n<MOD.mtfsizeact)
            {   bitreactivate(&(MOD.full),MOD.mtfhist[i].sym);
                MOD.lastseen[MOD.mtfhist[i].sym] = FULLFLAG;
                i = MOD.mtfhist[i].next;
                n++;
            }
            MOD.mtfsizeact = MTFSIZE;
        }
        else if (MOD.mtfsizeact < MTFSIZE) /* active MTF too small */
        {   uint n;
            mtfentry *pred;
            if (MOD.mtfsizeact==0)
            {   activatenext(&MOD, &(MOD.mtffirst));
                pred = MOD.mtfhist + MOD.mtffirst;
            }
            else
            {   pred = MOD.mtfhist + MOD.mtffirst;
                for(n=MOD.mtfsizeact-1; n; n--)
                    pred = MOD.mtfhist + pred->next;
            }
            while (MOD.mtfsizeact<MTFSIZE && activatenext(&(MOD), &(pred->next)))
                pred = MOD.mtfhist + pred->next;
        }
        sym = bitgetsym( &(MOD.full), decode_culfreq( &(MOD.ac), bittotf(&(MOD.full))));
        bitgetfreq( &(MOD.full), sym, &sy_f, &lt_f );
        decode_update(&(MOD.ac), sy_f, lt_f, bittotf(&(MOD.full)));
        bitupdate_ex(&(MOD.full), sym);
      { cacheptr free = MOD.newest->next;
        MOD.newest = free;
        free->what = 2;
        free->weight = readrun(MOD.rlemod, runlength);
        free->sy_f = free->weight;
      }
        *symbol = sym;
    }
    finishupdate(m, *symbol);
};


/* initialisation if the model */
/* headersize -1 means decompression */
/* first is the first byte written by the arithcoder */
void initmodel(sz_model *m, int headersize, unsigned char *first)
{   int i;

    /* init the arithcoder */
    if((MOD.compress = (headersize>=0)))
        start_encoding(&(MOD.ac),*first,headersize);
    else
        *first = start_decoding(&(MOD.ac));

    /* init the full model */
    initbitmodel(&(MOD.full), ALPHABETSIZE, 40*ALPHABETSIZE, 10*ALPHABETSIZE, NULL);
    for(i=0; i<ALPHABETSIZE; i++)
        MOD.lastseen[i] = FULLFLAG;

    /* init the cache with symbols CACHESIZE-1 to 0 */
  { cacheptr tmp = MOD.cache;
    for(i=0; i<CACHESIZE-1; i++)
    {   tmp->next = tmp+1;
        tmp->prev = tmp-1;
        tmp->symbol = CACHESIZE - 2 - i;
        MOD.lastseen[tmp->symbol] = tmp;
        bitdeactivate(&(MOD.full),tmp->symbol);
	tmp->sy_f = 1;
        tmp->weight = 1;
        tmp->what = 0;
        tmp++;
    }
    MOD.cache[0].prev = MOD.cache + (CACHESIZE-1);
    tmp->next = MOD.cache;
    tmp->prev = tmp-1;
    tmp->sy_f = 0;
  }
    MOD.newest = MOD.cache + (CACHESIZE-2);
    MOD.lastnew = MOD.cache + (CACHESIZE-7);
    MOD.cachetotf = CACHESIZE; // for starup only, decremented by 1 later
    /* initialize the whatmodel */
    MOD.whatmod[0] = 41; // 1 + 22*1 + 3*6
    MOD.whatmod[1] = 8;  // 1 + 1*1 + 1*6
    MOD.whatmod[2] = 15; // 1 + 2*1 + 2*6
    /* make 2 old and 2 new full hits for what */
    for(i=0; i<2; i++)
    {   MOD.cache[i].what = 2;
        MOD.lastnew[i].what = 2;
    }
    /* make 1 old and 1 new hit for MTF */
    MOD.cache[2].what = 1;
    MOD.lastnew[2].what = 1;

    
    /* init the mtf models with symbols CACHESIZE .. (CACHESIZE+MTFSIZE<<1)*/
    MOD.mtfhist[0].next = MTFHISTSIZE-1;
    MOD.mtfhist[0].sym = CACHESIZE;
    for(i=1; i<MTFSIZE<<1; i++)
    {   MOD.mtfhist[i].next = i-1;
        MOD.mtfhist[i].sym = CACHESIZE+i;
    }
    for(; i<MTFHISTSIZE; i++)
        MOD.mtfhist[i].next = 0xffff;
    MOD.mtfsize = MTFSIZE<<1;
    MOD.mtfsizeact = 0;
    MOD.mtffirst = (MTFSIZE<<1) - 1;
    initqsmodel(&(MOD.mtfmod),MTFSIZE,MTFSHIFT,400,NULL,MOD.compress);

    /* init the runlengthmodels */
    for(i=0; i<5; i++)
        initqsmodel(MOD.rlemod+i,7,RLSHIFT,150,NULL,MOD.compress);
}


/* call fixafterfirst after encoding/decoding the first run */
void fixafterfirst(sz_model *m)
{   MOD.cachetotf--;
}


/* deletion of the model */
void deletemodel(sz_model *m)
{   int i;
    if (MOD.compress)
        MOD.ac.bytecount = done_encoding(&(MOD.ac));
    else
        done_decoding(&(MOD.ac));

//fprintf(stderr,"%d %d %d ",MOD.ac.bytecount,MAXCACHESIZE,MTFSIZE);
//for(i=0; i<MTFSIZE; i++) fprintf(stderr,"%d ",modelused[i]);

    /* delete the fullmodel */
    deletebitmodel(&(MOD.full));

    /* delete the mtfmodel */
    deleteqsmodel(&(MOD.mtfmod));

    /* init the runlengthmodels */
    for(i=0; i<5; i++)
        deleteqsmodel(MOD.rlemod+i);
}

//#define CHECKINDIRECT

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
// #include "port.h"
// #include "sz_err.h"
// #include "sz_srt.h"

#ifndef verbosity
extern uint verbosity;
#endif

#if defined SZ_UNSRT_O4
// #include "sz_hash2.h"		// only used in sz_unsrt_o4
#endif

// the sorting is a little slow due to attempts to reuse memory as soon as possible.
// since the n-1 order sorted block is read sequentially a block can be freed (inserted
// in a freelist) as soon as it is processed. Since the new n-order sorted pointers
// grow as 256 different lists there is no need to have all memory available at once;
// new memory is needed at the same speed old is freed.

#define BITSSAMEBLOCK 10
#define BLOCKSIZE (1<<BITSSAMEBLOCK)
#define BLOCKMASK (BLOCKSIZE-1)

typedef struct p_block ptrblock;

struct p_block{
	uint2 msbytes[BLOCKSIZE];
	unsigned char lsbyte[BLOCKSIZE];
	ptrblock *nextfree;
};


typedef struct {
	ptrblock **index;		// index to blocks used in current sort
	ptrblock **oldindex;	// spare mem for alternate index
	ptrblock *freelist;
	ptrblock *block;
	ptrblock *spare[18];
	uint4 nrblocks;
} ptrstruct;


static ptrstruct globalptr;
static int globalinit = 0;

static void allocptrs(uint4 length, ptrstruct *p)
{	uint4 i;
	p->nrblocks = (length+BLOCKSIZE-1)/BLOCKSIZE;
	if (globalinit && (p->nrblocks>globalptr.nrblocks)) {
		free(globalptr.index);
		free(globalptr.oldindex);
		free(globalptr.block);
	    globalinit = 0;
	}
	if (!globalinit) {
		globalptr.nrblocks = p->nrblocks;
		globalptr.index = (ptrblock**) malloc(sizeof(ptrblock*)*globalptr.nrblocks);
		if (globalptr.index == NULL)
			sz_error(SZ_NOMEM_SORT);
		globalptr.oldindex = (ptrblock**) malloc(sizeof(ptrblock*)*globalptr.nrblocks);
		if (globalptr.oldindex == NULL)
			sz_error(SZ_NOMEM_SORT);
		globalptr.block = (ptrblock*) malloc(sizeof(ptrblock)*globalptr.nrblocks);
		if (globalptr.block == NULL)
			sz_error(SZ_NOMEM_SORT);
	    globalinit = 1;
	}
	p->index = globalptr.index;
	p->oldindex = globalptr.oldindex;
	p->block = globalptr.block;
	p->freelist = NULL;
	for(i=0; i<18; i++)
		p->spare[i] = NULL;
	for (i=0; i<p->nrblocks; i++)
		p->index[i] = p->block + i;
}

static void extraspare(ptrstruct *p, int blocks)
{	int i;
	for (i=0; p->spare[i]!= NULL; i++)
		/* void */;
	p->spare[i] = (ptrblock*) malloc(sizeof(ptrblock)*blocks);
	if (p->spare[i] == NULL)
		sz_error(SZ_NOMEM_SORT);
	p->spare[i]->nextfree = p->freelist;
	p->freelist = p->spare[i];
	for(i=1; i<blocks; i++)
		p->freelist[i-1].nextfree = p->freelist + i;
	p->freelist[blocks-1].nextfree = NULL;
}

static void allocspareptrs(uint4 length, ptrstruct *p)
{	length = (length>>BITSSAMEBLOCK) + 1;
	if (length>256) length = 256;
	extraspare(p,length);
}

static void freeptrs(ptrstruct *p)
{	int i;
//	free(p->index);
//	free(p->oldindex);
//	free(p->block);
	for (i=0; p->spare[i] != NULL; i++)
		free(p->spare[i]);
}

static Inline void setptr(ptrstruct *p, uint4 i, uint4 ptr)
{	ptrblock *tmp;
	tmp = p->index[i>>BITSSAMEBLOCK];
	if (tmp==NULL)
	{	if (p->freelist == NULL)
			extraspare(p,16);
		tmp = p->index[i>>BITSSAMEBLOCK] = p->freelist;
		p->freelist = p->freelist->nextfree;
	}
	i &= BLOCKMASK;
	tmp->msbytes[i] = ptr>>8;
	tmp->lsbyte[i] = ptr & 0xff;
}

static void sortorder2(ptrstruct *p, unsigned char *in, uint4 length,
					   uint4 *counts, unsigned int offset, uint4 *indexlast)
{	uint4 i, *o2counts, sum;
	unsigned int context;
	memset(counts, 0, 256*sizeof(uint4));
	o2counts = (uint4*) calloc(0x10000, sizeof(uint4));
	if (o2counts == NULL)
		sz_error(SZ_NOMEM_SORT);
	context = (unsigned)in[length-1]<<8;
	for(i=0; i<length; i++)
	{	context = context>>8 | (unsigned)(in[i])<<8;
		counts[in[i]]++;
		o2counts[context]++;
	}
	sum = length;
	for (i=0x10000; i--; )
	{	sum -= o2counts[i];
		o2counts[i] = sum;
	}
	sum = length;
	for (i=0x100; i--; )
	{	sum -= counts[i];
		counts[i] = sum;
	}
	context = (unsigned)in[length-offset]<<8 | in[length-offset-1];
	if (context == 0xffff)
		*indexlast = length-1;
	else
		*indexlast = o2counts[context+1]-1;
	offset--;
	for(i=0; i<offset; i++)
	{	in[i+length] = in[i];
		context = context>>8 | (unsigned int)(in[i+length-offset])<<8;
		setptr(p,o2counts[context],i+length);
		o2counts[context]++;
	}
	for(i=offset; i<length; i++)
	{	context = context>>8 | (unsigned int)(in[i-offset])<<8;
		setptr(p,o2counts[context],i);
		o2counts[context]++;
	}
	free(o2counts);
}

static void incsortorder(ptrstruct *p, unsigned char *in, uint4 length,
						 uint4 *counts, int offset, uint4 *indexlast)
{	uint4 i, block, ct[256];
	ptrblock *curblock;
	unsigned char ch=0;
	{ptrblock **swap=p->index; p->index = p->oldindex; p->oldindex = swap;}
	memset(p->index,0,p->nrblocks*sizeof(ptrblock*));
	memcpy(ct,counts,256*sizeof(uint4));
	block = 0;
	curblock = p->oldindex[block];
	for (i=0; i<=*indexlast; i++)
	{	unsigned index = i & BLOCKMASK;
		uint4 tmp = (uint4)(curblock->msbytes[index])<<8 | curblock->lsbyte[index];
		ch = in[tmp-offset];
		setptr(p,ct[ch],tmp);
		ct[ch]++;
		if (index==BLOCKMASK && block!=p->nrblocks-1)		//last ptr in block
		{	curblock->nextfree = p->freelist;
			p->freelist = curblock;
			block++;
			curblock = p->oldindex[block];
		}
	}
	*indexlast = ct[ch]-1;
	for ( ; i<length; i++)
	{	unsigned index = i & BLOCKMASK;
		uint4 tmp = (uint4)(curblock->msbytes[index])<<8 | curblock->lsbyte[index];
		ch = in[tmp-offset];
		setptr(p,ct[ch],tmp);
		ct[ch]++;
		if (index==BLOCKMASK && block<p->nrblocks-1)		//last ptr in block
		{	curblock->nextfree = p->freelist;
			p->freelist = curblock;
			block++;
			curblock = p->oldindex[block];
		}
	}
	curblock->nextfree = p->freelist;
	p->freelist = curblock;
}


static void finishsort(ptrstruct *p, unsigned char *in, uint4 length,
						 uint4 *counts, uint4 *indexlast)
{	uint4 i, block, ct[256];
	ptrblock *curblock;
	unsigned char ch=0;
	{ptrblock **swap=p->index; p->index = p->oldindex; p->oldindex = swap;}
	memset(p->index,0,p->nrblocks*sizeof(ptrblock*));
	memcpy(ct,counts,256*sizeof(uint4));
	block = 0;
	curblock = p->oldindex[block];
	for (i=0; i<=*indexlast; i++)
	{	unsigned index = i & BLOCKMASK;
		uint4 tmp = (uint4)(curblock->msbytes[index])<<8 | curblock->lsbyte[index];
		ch = in[tmp-1];
		setptr(p,ct[ch],in[tmp]);
		ct[ch]++;
		if (index==BLOCKMASK && block!=p->nrblocks-1)		//last ptr in block
		{	curblock->nextfree = p->freelist;
			p->freelist = curblock;
			block++;
			curblock = p->oldindex[block];
		}
	}
	*indexlast = ct[ch]-1;
	for ( ; i<length; i++)
	{	unsigned index = i & BLOCKMASK;
		uint4 tmp = (uint4)(curblock->msbytes[index])<<8 | curblock->lsbyte[index];
		ch = in[tmp-1];
		setptr(p,ct[ch],in[tmp]);
		ct[ch]++;
		if (index==BLOCKMASK && block!=p->nrblocks-1)		//last ptr in block
		{	curblock->nextfree = p->freelist;
			p->freelist = curblock;
			block++;
			curblock = p->oldindex[block];
		}
	}
	curblock->nextfree = p->freelist;
	p->freelist = curblock;
	for (i=0; i<p->nrblocks-1; i++)
		memcpy(in+i*BLOCKSIZE, p->index[i]->lsbyte, BLOCKSIZE);
	i= p->nrblocks - 1;
	memcpy(in+BLOCKSIZE*i, p->index[i]->lsbyte, length-i*BLOCKSIZE);
}


// inout: bytes to be sorted; sorted bytes on return. must be length+order bytes long
// length: number of bytes in inout
// *indexlast: returns position of last context (needed for unsort)
// order: order of context used in sorting (must be >=3)
// the code assumes length>=order
// and inout is length+order bytes long (only the first length need to be filled)
void sz_srt(unsigned char *inout, uint4 length, uint4 *indexlast, unsigned int order)
{	uint4 i;
	ptrstruct p;
	uint4 counts[256];
	allocptrs(length, &p);
	sortorder2(&p, inout, length, counts, order, indexlast);
	allocspareptrs(length, &p);
	for (i=order-2; i>1; i--)
		incsortorder(&p, inout, length, counts, i, indexlast);
	finishsort(&p, inout, length, counts, indexlast);
	freeptrs(&p);
}


#define INDIRECT 0x800000

#define setbit(flags,bit) (flags[bit>>3] |= 1<<(bit & 7))
#define getbit(flags,bit) ((flags[bit>>3]>>(bit&7)) & 1)

static void makeorder2(unsigned char *flags, unsigned char *in, uint4 *counts,
					   uint4 length)
{	uint4 i, j, ct[256];
	memcpy(ct, counts, 256*sizeof(uint4));
	// set bits in flag1 at start of each order 2 context
	// for order 2 this is more efficient than the method used for higher orders
	for(i=0; i<256; i++)
	setbit(flags,ct[i]);
	j = 0;
	for (i=0; i<255; i++)
	{	uint4 k;
		for(k=counts[i+1]; j<k; j++)
			ct[in[j]]++;
		for(k=0; k<256; k++)
			setbit(flags,ct[k]);
	}
}


static void increaseorder(unsigned char *inflags, unsigned char *outflags,
						  unsigned char *in, uint4 *counts, uint4 length)
{	uint4 i, contextstart, lastseen[256], ct[256];
	memcpy(ct, counts, 256*sizeof(uint4));
	contextstart = 0;
	memset(lastseen, 0xff, 256*sizeof(uint4)); 
	for (i=0; i<length; i++)
	{	int ch;
		if (getbit(inflags, i))			// ch = -1 + getbit(inflags,i);
			contextstart = i;			// contextstart = (contextstart&ch) | (i&~ch);
		ch = in[i];
		if (lastseen[ch] != contextstart)	// use a bitfield instead of lastseen
		{	lastseen[ch] = contextstart;	// in hardware!
			setbit(outflags, ct[ch]);
		}
		ct[ch]++;
	}
}


static void maketable(unsigned char *inflags, uint4 *table, unsigned char *in,
					  uint4 *counts, uint4 length)
{	uint4 i, contextstart, firstseen[256], ct[256];
	memcpy(ct, counts, 256*sizeof(uint4));
	contextstart = 0;
	memset(firstseen, 0, 256*sizeof(uint4)); 
	for (i=0; i<length; i++)
	{	int ch;
		if (getbit(inflags, i))
			contextstart = i;
		ch = in[i];
		if (firstseen[ch] <= contextstart)
		{	table[i] = ct[ch];
			firstseen[ch] = i+1;
		}
		else
			table[i] = (firstseen[ch]-1) | INDIRECT;
		ct[ch]++;
	}
}

// in: bytes to be unsorted
// out: unsorted bytes; if out==NULL output is written to stdout
// length: number of bytes in in (and out)
// indexlast: position of last context (as returned bt sorttrans)
// counts: number of occurances of each byte in in (if NULL it will be calculated)
// order: order of context used in sorting (must be >=3)
// the code assumes length>=order
void sz_unsrt(unsigned char *in, unsigned char *out, uint4 length, uint4 indexlast,
			uint4 *counts, unsigned int order)
{	uint4 i, j;
    static uint4 *table;
	static unsigned char *flags1=NULL;
	static unsigned char *flags2=NULL;
	unsigned char nocounts;

	// get counts if not supplied
	nocounts = counts==NULL;
	if (nocounts)
	{	counts = (uint4*) calloc(256, sizeof(uint4));
		for (i=0; i<length; i++)
			counts[in[i]]++;
	}
	// sum counts
	j = length;
	for (i=256; i--; )
	{	j -= counts[i];
		counts[i] = j;
	}

	if (flags1==NULL){
		flags1 = (unsigned char*) calloc((length+8)>>3,1);
		if (flags1 == NULL)
			sz_error(SZ_NOMEM_SORT);
	} else 
		memset(flags1,0,(length+8)>>3);

	makeorder2(flags1, in, counts, length);
	
	// now incease the order to desired order-1
	if (flags2==NULL){
		flags2 = (unsigned char*) calloc((length+8)>>3,1);
		if (flags2 == NULL)
			sz_error(SZ_NOMEM_SORT);
	} else 
		memset(flags2,0,(length+8)>>3);
	for (i=2; i<order-1; i++)
	{	unsigned char *tmpflags;
		increaseorder(flags1, flags2, in, counts, length);
		tmpflags = flags1;
		flags1 = flags2;		// flags1 now contains the updated beginflags
		flags2 = tmpflags;		// no need to clear, the set bits will be set again
	}
//	free(flags2);

	// construct permutation table
	if (table==NULL) {
		table = (uint4*)malloc((length+1)*sizeof(uint4));
		if (table == NULL)
			sz_error(SZ_NOMEM_SORT);
	}
	maketable(flags1, table, in, counts, length);
	table[length] = INDIRECT;
//	free(flags1);
	if (nocounts)
		free(counts);

	// do the actual unsorting
	j = indexlast;
	if (out == NULL)
		for (i=0; i<length; i++)
		{	uint4 tmp = table[j];
			if (tmp & INDIRECT)
			{	j = table[tmp & ~INDIRECT]++;
#ifdef CHECKINDIRECT
				if (j&INDIRECT)
					sz_error(SZ_DOUBLEINDIRECT);
#endif
			}
			else
			{	table[j]++;
				j = tmp;
			}
			putc(in[j],stdout);
		}
	else
		for (i=0; i<length; i++)
		{	uint4 tmp = table[j];
			if (tmp & INDIRECT)
				j = table[tmp & ~INDIRECT]++;
			else
			{	table[j]++;
				j = tmp;
			}
			out[i] = in[j];
		}

	if (j != indexlast)
		sz_error(SZ_NOTCYCLIC);
//	free(table);
}


#if defined SZ_SRT_O4
// a fast alternate sort, only for order 4. inout only length bytes is OK here.
void sz_srt_o4(unsigned char *inout, uint4 length, uint4 *indexlast)
{	static uint4 *counters=NULL;
	static uint2 *context=NULL;
	static unsigned char *symbols=NULL;
	register uint4 i;

	// count contexts
	if (counters==NULL) {
		counters = (uint4*)calloc(0x10000,sizeof(uint4));
		if (counters == NULL)
			sz_error(SZ_NOMEM_SORT);
	} else {
		memset(counters,0,0x10000*sizeof(uint4));
	}
	i = (uint)(inout[length-1])<<8;
  {	register unsigned char *tmp;
	for (tmp=inout; tmp<inout+length; tmp++)
	{	i = i>>8 | (uint)(*tmp)<<8;
		counters[i]++;
	}
  }

	// add context counts
  {	register uint4 sum = length;
	for (i=0x10000; i--; )
	{	sum -= counters[i];
		counters[i] = sum;
	}
  }

	// first sort pass
    if (context==NULL) {
		context = (uint2*)malloc(length*sizeof(uint2));
		if (context == NULL)
			sz_error(SZ_NOMEM_SORT);
	}
	if (symbols==NULL) {
		symbols = (unsigned char*)(malloc(length));
		if (symbols == NULL)
			sz_error(SZ_NOMEM_SORT);
	}

	// the following loop in assembler it would probably be a lot faster
  {	register unsigned char *tmp;
	register uint4 ctx = (uint4)inout[length-4]<<8 | inout[length-5];
	if (ctx == 0xffff)
		*indexlast = length-1;
	else
		*indexlast = counters[ctx+1]-1;
	ctx = (((uint4)inout[length-1] << 8 | inout[length-2]) << 8 |
		    inout[length-3]) << 8 | inout[length-4];
	for (tmp=inout; tmp<inout+length; tmp++)
	{	register uint4 x = counters[ctx&0xffff]++;
		context[x] = ctx >> 16;
		ctx = ctx>>8 | (uint4)(symbols[x] = *tmp)<<24;
	}
  }

	/* second sort pass */
  {	uint4 lastpos = *indexlast;
	for (i=length; i>lastpos; )		// lastpos is the last processed in this loop
	{	i-=1;
		inout[--counters[context[i]]] = symbols[i];
	}
  }
	*indexlast = counters[context[i]];
	while (i--)
		inout[--counters[context[i]]] = symbols[i];

//	free(counters);
//	free(context);
//	free(symbols);
}
#endif


#ifdef SZ_UNSRT_O4
// an alternate backtransform for order 4 using hash tables
void sz_unsrt_o4(unsigned char *in, unsigned char *out, uint4 length, uint4 indexlast,
			   uint4 *counts)
{	uint4 i, *contexts2, *contexts4, initcontext;
	uint2 *lastseen;
	unsigned char *loop, *endloop, nocounts;
	h2table htable;

	// get counts if not supplied
	nocounts = counts==NULL;
	if (nocounts)
	{	counts = (uint4*) calloc(256, sizeof(uint4));
		for (i=0; i<length; i++)
			counts[in[i]]++;
	}
	
	// allocate tables (could do on stack, but will cause problems with some compilers
	contexts2 = (uint4*)calloc(0x10000, sizeof(uint4));
	if (contexts2 == NULL)
		sz_error(SZ_NOMEM_SORT);

	// count contexts
	loop = in;
	for (i=0; i<0x100; i++)
		for (endloop = loop+counts[i]; loop<endloop; loop++)
			contexts2[(unsigned int)(*loop)<<8 | i]++;
		
	// put sum of order2 contexts in order 4 contexts
	contexts4 = (uint4*)malloc(0x10000*sizeof(uint4));
	if (contexts4 == NULL)
		sz_error(SZ_NOMEM_SORT);
  {	uint4 sum = length;
	for (i=0x10000; i--;)
	{	if (sum > indexlast)
			initcontext = i;
		sum -= contexts2[i];
		contexts4[i] = sum;
	}
	initcontext <<= 16;
	// sum counts
	sum = length;
	for (i=0x100; i--;)
	{	sum -= counts[i];
		counts[i] = sum;
	}
  }

	initHash2(htable);

	// in hardware: make lastseen a bitfield and zero them all when you hit a new
	// order 2 context. set them whenever you see a new order 4 context.
	// much like in the loop for the 0x????0000 contexts.

	// loop over all order 2 contexts
	// count contexts 0x????0000 first
	loop = in;
	lastseen = (uint2*)calloc(0x10000,sizeof(uint2));
	if (lastseen == NULL)
		sz_error(SZ_NOMEM_SORT);
	for (endloop = loop+contexts2[0]; loop<endloop; loop++)
	{	uint4 j, tmp = (uint4)(*loop);
		j = counts[tmp]++;
		tmp |= (uint4)(in[j])<<8;
		if (!lastseen[tmp])
		{	lastseen[tmp] = 1;
			h2_insert(htable, tmp<<16, contexts4[tmp]);
		}
		contexts4[tmp]++;
	}

	
	// and now all others (couldnt do it in one because of lastseens limited size)
	memset(lastseen, 0, 0x10000*sizeof(uint2));		// zero lastseen again
	for (i=1; i<0x10000; i++)
	{	if (indexlast >= contexts4[initcontext>>16])
			initcontext = (initcontext & 0xffff0000) | i;
		for (endloop = loop+contexts2[i]; loop<endloop; loop++)
		{	uint4 j, tmp = (uint4)(*loop);
			j = counts[tmp]++;
			tmp |= (uint4)(in[j])<<8;
			if (lastseen[tmp] != i)
			{	lastseen[tmp] = i;
				h2_insert(htable, tmp<<16 | i, contexts4[tmp]);
			}
			contexts4[tmp]++;
		}
	}

	free(contexts2);
	free(contexts4);
	free(lastseen);
	if (nocounts)
		free(counts);

	// do the actual unsorting
	initcontext = initcontext>>8 | (uint4)in[indexlast]<<24;
  {	uint4 context = initcontext;
	if (out == NULL)
		for ( i=0; i<length; i++ )
		{	unsigned char outchar;
			outchar = in[h2_get_inc(htable, context)];
			context = (context>>8) | ((uint4)outchar<<24);
			putc(outchar, stdout);
		}
	else
		for ( i=0; i<length; i++ )
		{	unsigned char outchar;
			out[i] = outchar = in[h2_get_inc(htable, context)];
			context = (context>>8) | ((uint4)outchar<<24);
		}

	if (context != initcontext)
		sz_error(SZ_NOTCYCLIC);
  }
	freeHash2(htable);
}
#endif


#ifdef SZ_SRT_BW

// #include "qsort_u4.c"

void sz_srt_BW(unsigned char *inout, uint4 length, uint4 *indexfirst)
{	uint4 i, counts[256], counts1[256], *contextp, start;

	for (i=0; i<256; i++)
		counts[i] = 0;
	for (i=0; i<length; i++)
		counts[inout[i]]++;
	counts1[0] = 0;
	for (i=0; i<255; i++) 
		counts1[i+1] = counts1[i] + counts[i];
	
	contextp = (uint4*) calloc(length, sizeof(uint4));
	if (contextp == NULL)
		sz_error(SZ_NOMEM_SORT);

	for (i=0; i<length; i++)
		contextp[counts1[inout[i]]++] = i;

	start = 0;
	for (i=0; i<256; i++)
    {   if (verbosity&1) fputc((char)('0'+i%10),stderr);
        if (counts[i])
        {	qsort_u4(contextp+start, counts[i], inout, i==inout[0]?0:1);
			if (i==inout[length-1]) // search for indexfirst
			{	uint4 j=start;
                while(contextp[j]!=(length-1))
                    j++;
				*indexfirst = j;
			}
            start += counts[i];
		}
    }

	contextp[*indexfirst] = 0;
	for(i=0; i<length; i++)
		contextp[i] = inout[contextp[i]+1];
	contextp[*indexfirst] = inout[0];
	for(i=0; i<length; i++)
		inout[i] = contextp[i];

	free(contextp);
}


void sz_unsrt_BW(unsigned char *in, unsigned char *out, uint4 length,
			   uint4 indexfirst, uint4 *counts)
{	uint4 i, *transvec;
	unsigned char nocounts;

	// get counts if not supplied
	nocounts = counts==NULL;
	if (nocounts)
	{	counts = (uint4*) calloc(256, sizeof(uint4));
		if (counts == NULL)
			sz_error(SZ_NOMEM_SORT);
		for (i=0; i<length; i++)
			counts[in[i]]++;
	}
    
  {	uint4 sum = length;
	for (i=0x100; i--; )
	{	sum -= counts[i];
		counts[i] = sum;
	}
  }

	// prepare transposition vector
	transvec = (uint4*)malloc((length)*sizeof(uint4));
	if (transvec == NULL)
		sz_error(SZ_NOMEM_SORT);

	transvec[indexfirst] = counts[in[indexfirst]]++;
	for (i=0; i<indexfirst; i++)
		transvec[i] = counts[in[i]]++;
	for (i=indexfirst+1; i<length; i++)
		transvec[i] = counts[in[i]]++;


	if (nocounts)
		free(counts);

	// undo the blocksort
  {	uint4 ic=indexfirst;
	if (out==NULL)
		for (i=0; i<length; i++)
		{	putc(in[ic], stdout);
			ic = transvec[ic];
		}
	else
		for (i=0; i<length; i++)
		{	out[i] = in[ic];
			ic = transvec[ic];
		}
	if (ic != indexfirst)
		sz_error(SZ_NOTCYCLIC);
  }
	free(transvec);
}
#endif
