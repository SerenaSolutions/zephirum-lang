/* zephirum.h - C API of the ZYQL trivalent decision core (v1.4.3).
 *
 * Three layers: languages (Zephyron and bindings) -> THIS C API -> core.
 * The core decides by Deutsch-Jozsa interference with a declared noise
 * band and seals every verdict with ML-DSA-44 (FIPS 204).
 *
 * Decision values: 1 (permitted), 0 (forbidden), ZYQL_REFUSED (-1).
 */
#ifndef ZEPHIRUM_H
#define ZEPHIRUM_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque handle: one interference gate instance over n input qubits. */
typedef struct zyql_gate zyql_gate;

typedef enum {
    ZYQL_OK = 0,
    ZYQL_ERR_ALLOC = 1,
    ZYQL_ERR_NO_CLONING = 2,   /* type system: quantum value copied */
    ZYQL_ERR_BAD_PURPOSE = 3,  /* purpose function outside {0,1} */
    ZYQL_ERR_INSIDE_BAND = 4   /* honest refusal: insufficient confidence */
} zyql_status;

/* Lifecycle. `n` input qubits, 1 <= n <= 32. */
zyql_status zyql_gate_new(zyql_gate **g, uint32_t n);
void        zyql_gate_free(zyql_gate *g);

/* Register a purpose function f: {0,1}^n -> {0,1}. One registration. */
zyql_status zyql_gate_set_purpose(zyql_gate *g,
                                  int (*f)(uint64_t x, void *ctx), void *ctx);

/* Interference decision. Exactly ONE oracle call.
 * Writes the measured p0 (probability of |0..0>), the verdict
 * (1 / 0 / ZYQL_REFUSED) and the declared margin into *out. */
zyql_status zyql_decide(zyql_gate *g,
                        uint32_t shots,
                        double   *out_p0,
                        int32_t  *out_verdict,
                        double   *out_margin);

/* Receipt: canonical rational certificate (num/den, no 17-digit floats). */
typedef struct {
    int64_t  p0_num, p0_den;
    int32_t  verdict;
    uint32_t oracle_calls;
    uint32_t shots;
    char     ml_dsa_44_sig[512];  /* FIPS 204 signature over fields above */
} zyql_receipt;

zyql_status zyql_get_receipt(const zyql_gate *g, zyql_receipt *out);

/* Noise band: declared, not hidden. */
#define ZYQL_NOISE_BAND 0.15
#define ZYQL_REFUSED   (-1)

#ifdef __cplusplus
}
#endif
#endif /* ZEPHIRUM_H */
