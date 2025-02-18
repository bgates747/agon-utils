#ifndef SIMZ_H
#define SIMZ_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef GCC
#define Inline inline
#else
#define Inline __inline
#endif

typedef unsigned short uint2;  /* two-byte integer (for large arrays) */
typedef unsigned int   uint4;  /* four-byte integer (range needed)      */
typedef unsigned int   uint;   /* fast unsigned integer, 2 or 4 bytes     */

#ifdef __cplusplus
}
#endif

#endif // SIMZ_H
