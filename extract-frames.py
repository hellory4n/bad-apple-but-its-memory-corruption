# requirements:
# - a linux desktop
# - ffmpeg
# - clang
# - pip install ffmpeg-python
# - pip install pillow
#
# usage: python extract-frames.py [bad apple mp4]
# all frames will be outputted into a frames/ directory

import glob
import os
import sys
import subprocess
import ffmpeg
from PIL import Image

os.makedirs("frames", exist_ok=True)

# extract frames into images
if not os.path.exists("frames/frame_0001.png"):
    (
        ffmpeg.input(sys.argv[1])
        .filter("fps", fps=10) # the resolution is too shitty to notice
        .output("frames/frame_%04d.png")
        .run()
    )

# load the fucking frames
frames = sorted(glob.glob("frames/frame_*.png"))
for frame in frames:
    img = Image.open(frame)

    # incredible resolution we're working with
    img_resized = img.resize((15, 11))

    pixels = img_resized.load()
    assert pixels is not None

    # generate amazing code
    with open(frame.replace(".png", ".c"), "w") as f:
        f.write(
"""
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
"""
        )

        # the important part
        for x in range(15):
            for y in range(11):
                pixel = pixels[x, y]
                if pixel[0] < 127:
                    f.write(f"BLACK({x}, {y});\n")

        f.write(
"""
    // trigger error message
    GET_PIXEL(WIDTH - 1, HEIGHT / 2) = 0;

    free(buf);
}"""
        )

    # i am compiling it
    print(subprocess.run(
        f"clang -std=c99 -Wall -Wextra -Wpedantic -fsanitize=address {frame.replace('.png', '.c')} -o {frame.replace('.png', '')}",
        shell=True,
        capture_output=True,
        text=True
    ).stdout)
    # i am running it
    # grep for nicer output and so you don't have to scroll to screenshot
    print(subprocess.run(
        f"bash -c ./{frame.replace('.png', '')} 2>&1 > /dev/null | grep 0x --color=never | grep --color=always f7",
        shell=True,
        capture_output=True,
        text=True
    ).stdout)
    # the fucking screenshot fuckery
    print(subprocess.run(
        f"grim - > {frame.replace('frame_', 'screenshot_')}",
        shell=True,
        capture_output=True,
        text=True
    ).stdout)

    print(f"frame {frame.replace('frames/frame_', '').replace('.png', '')}")
