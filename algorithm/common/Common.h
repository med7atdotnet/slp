#ifndef SLP_COMMON_H
#define SLP_COMMON_H

#include "pp.h"

#define BOTTOM (-1)

#define UNKNOWN_SEQNO (-1LL)

#define ARRAY_LENGTH(arr) (sizeof(arr) / sizeof(arr[0]))

#define max(a, b) \
	({ __typeof__(a) _a = (a), _b = (b); \
	   _a > _b ? _a : _b; })

#define min(a, b) \
	({ __typeof__(a) _a = (a), _b = (b); \
	   _a < _b ? _a : _b; })

#define min3(a, b, c) \
	({ __typeof__(a) _m1 = min(a, b), _c = (c); \
	   _m1 < _c ? _m1 : _c; })

#define minbot(a, b) \
	({ __typeof__(a) _a = (a), _b = (b); \
	   (_a == BOTTOM ? _b : (_b == BOTTOM ? _a : (_b < _a ? _b : _a))); })


inline int16_t botinc(int16_t x)
{
	return x == BOTTOM ? BOTTOM : x + 1;
}

inline double rad2deg(double r)
{
	return r * (180.0 / M_PI);
}

// Disable using assert when running on real hardware 
#ifndef TESTBED
#	include <assert.h>
#else
#	define assert(...)
#endif

// Compiling for testbeds, so need to route the simdbg to the printf library
#ifdef USE_SERIAL_PRINTF
#	include "printf.h"
#endif

#if defined(USE_SERIAL_PRINTF) || defined(USE_SERIAL_MESSAGES)
#	define sim_time_string() STATIC_ASSERT_MSG(FALSE, "sim_time_string is forbidden to be used with USE_SERIAL_PRINTF or USE_SERIAL_MESSAGES")
#	define sim_time() STATIC_ASSERT_MSG(FALSE, "sim_time is forbidden to be used with USE_SERIAL_PRINTF or USE_SERIAL_MESSAGES")
#endif

#ifndef PRIu8
#	define PRIu8 "u"
#endif

#ifndef PRIu64
#	define PRIu64 "llu"
#endif

#ifndef PRIi64
#	define PRIi64 "lld"
#endif

#ifdef SLP_VERBOSE_DEBUG
#	define simdbgverbose(...) simdbg(__VA_ARGS__)
#else
#	define simdbgverbose(...)
#endif

#endif // SLP_COMMON_H
