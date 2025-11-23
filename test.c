#ifndef __clang__
	#error "only clang is supported"
#endif

#ifdef __has_feature
	#if !__has_feature(address_sanitizer)
		#error "enable asan immediately"
	#endif
#else
	#error "where __has_feature"
#endif

#include <sanitizer/asan_interface.h>
#include <stdint.h>
#include <stdlib.h>

#define WIDTH 16
#define HEIGHT 11

int main(void)
{
	// asan shows the bytes as 8 byte chunks
	uint64_t* buf = malloc(sizeof(uint64_t) * WIDTH * HEIGHT);
#define GET_PIXEL(x, y) buf[y * WIDTH + x]
#define BLACK(x, y) __asan_poison_memory_region(&GET_PIXEL(x, y), sizeof(uint64_t))

	// set black parts
	// these are outside of the frame (as the aspect ratio doesn't match exactly)
	for (int y = 0; y < HEIGHT; y++) {
		BLACK(WIDTH - 1, y);
	}

	BLACK(5, 3);
	BLACK(5, 4);
	BLACK(5, 5);
	BLACK(5, 6);
	BLACK(5, 7);
	BLACK(6, 5);
	BLACK(7, 3);
	BLACK(7, 4);
	BLACK(7, 5);
	BLACK(7, 6);
	BLACK(7, 7);

	// trigger error message
	GET_PIXEL(WIDTH - 1, HEIGHT / 2) = 0;

	free(buf);
}
