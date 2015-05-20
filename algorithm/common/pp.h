#ifndef SLP_PP_H
#define SLP_PP_H

/*
 * Concatenate preprocessor tokens A and B without expanding macro definitions
 * (however, if invoked from a macro, macro arguments are expanded).
 */
#define PPCAT_NX(A, B) A ## B

/*
 * Concatenate preprocessor tokens A and B after macro-expanding them.
 */
#define PPCAT(A, B) PPCAT_NX(A, B)

#define ARRAY_SIZE(a) (sizeof(a) / sizeof(*a))

#define CHAR_BIT 8

#endif // SLP_PP_H
