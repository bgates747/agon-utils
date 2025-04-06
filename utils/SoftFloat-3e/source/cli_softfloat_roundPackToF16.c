#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include "softfloat.h"    // Ensure this header declares needed softfloat functions/flags.
#include "internals.h"    // If needed for debugging prints and softfloat internals.

float16_t cli_softfloat_roundPackToF16(bool sign, int_fast16_t exp, uint_fast16_t sig)
{
    uint_fast8_t roundingMode;
    bool roundNearEven;
    uint_fast8_t roundIncrement, roundBits;
    bool isTiny;
    uint_fast16_t uiZ;
    union ui16_f16 uZ;

    /*------------------------------------------------------------------------
     * Initialize rounding mode and determine round increment.
     *------------------------------------------------------------------------*/
    roundingMode = softfloat_roundingMode;
    roundNearEven = (roundingMode == softfloat_round_near_even);
    roundIncrement = 0x8;
    if (!roundNearEven && (roundingMode != softfloat_round_near_maxMag)) {
        roundIncrement =
            (roundingMode == (sign ? softfloat_round_min : softfloat_round_max))
                ? 0xF
                : 0;
    }
    roundBits = sig & 0xF;

    /*------------------------------------------------------------------------
     * Process exponent and adjust sig if necessary.
     *------------------------------------------------------------------------*/
    if (0x1D <= (unsigned int) exp) {
        if (exp < 0) {
            isTiny =
                (softfloat_detectTininess == softfloat_tininess_beforeRounding)
                    || (exp < -1) || (sig + roundIncrement < 0x8000);
            sig = softfloat_shiftRightJam32(sig, -exp);
            printf("exp=0x%02x sig=0x%04x sig shifted right with shift count -exp\n",
                   (unsigned int)(exp & 0xFF), (unsigned int)sig);
            exp = 0;
            printf("exp=0x%02x sig=0x%04x exp set to zero due to negative exponent\n",
                   (unsigned int)exp, (unsigned int)sig);
            roundBits = sig & 0xF;
            if (isTiny && roundBits) {
                softfloat_raiseFlags(softfloat_flag_underflow);
                printf("exp=0x%02x sig=0x%04x underflow: raising underflow flag\n",
                       (unsigned int)exp, (unsigned int)sig);
            }
        } else if ((0x1D < exp) || (0x8000 <= sig + roundIncrement)) {
            softfloat_raiseFlags(softfloat_flag_overflow | softfloat_flag_inexact);
            printf("exp=0x%02x sig=0x%04x overflow: raising overflow/inexact flags and setting result to max\n",
                   (unsigned int)exp, (unsigned int)sig);
            uiZ = packToF16UI(sign, 0x1F, 0) - !roundIncrement;
            goto uiZ;
        }
    }

    /*------------------------------------------------------------------------
     * Final rounding steps.
     *------------------------------------------------------------------------*/
    sig = (sig + roundIncrement) >> 4;
    printf("exp=0x%02x sig=0x%04x sig updated after adding roundIncrement and shifting right by 4\n",
           (unsigned int)exp, (unsigned int)sig);
    if (roundBits) {
        softfloat_exceptionFlags |= softfloat_flag_inexact;
#ifdef SOFTFLOAT_ROUND_ODD
        if (roundingMode == softfloat_round_odd) {
            sig |= 1;
            printf("exp=0x%02x sig=0x%04x sig updated with odd rounding (OR 1)\n",
                   (unsigned int)exp, (unsigned int)sig);
            goto packReturn;
        }
#endif
    }
    sig &= ~(uint_fast16_t)(!(roundBits ^ 8) & roundNearEven);
    printf("exp=0x%02x sig=0x%04x sig masked for round near even adjustment\n",
           (unsigned int)exp, (unsigned int)sig);
    if (!sig) {
        exp = 0;
        printf("exp=0x%02x sig=0x%04x exp set to zero because sig is zero\n",
               (unsigned int)exp, (unsigned int)sig);
    }
packReturn:
    uiZ = packToF16UI(sign, exp, sig);
uiZ:
    uZ.ui = uiZ;
    return uZ.f;
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s sign exp sig\n", argv[0]);
        return EXIT_FAILURE;
    }

    unsigned int sign_val_u, exp_val_u, sig_val;
    if (sscanf(argv[1], "%x", &sign_val_u) != 1 ||
        sscanf(argv[2], "%x", &exp_val_u) != 1 ||
        sscanf(argv[3], "%x", &sig_val) != 1) {
        fprintf(stderr, "Error: Invalid hex value.\n");
        return EXIT_FAILURE;
    }

    // Interpret sign and exponent as signed 8-bit, then cast to wider signed type.
    int8_t sign8 = (int8_t)(uint8_t)sign_val_u;
    int8_t exp8  = (int8_t)(uint8_t)exp_val_u;

    bool sign = (sign8 < 0);
    int_fast16_t exp = (int_fast16_t)exp8;
    uint_fast16_t sig = (uint_fast16_t)sig_val;

    float16_t result = cli_softfloat_roundPackToF16(sign, exp, sig);

    union ui16_f16 conv;
    conv.f = result;
    uint16_t result_ui = conv.ui;

    printf("Input: sign=0x%02x, exp=0x%02x, sig=0x%04x\n", (uint8_t)sign_val_u, (uint8_t)exp_val_u, sig_val);
    printf("Interpreted: sign=%d, exp=%d (0x%04x), sig=0x%04x\n", sign, exp, (uint16_t)exp, sig);
    printf("Output: 0x%04x\n", result_ui);

    return EXIT_SUCCESS;
}
