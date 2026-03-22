# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow"]
# ///
"""Convert a static image into a seamlessly looping scrolling GIF animation.

The image is converted to black-and-white and scrolls continuously
right-to-left with seamless wrapping.
"""

import argparse
from pathlib import Path

from PIL import Image


def find_scroll_speed(tile_w: int, fps: int) -> int:
    """Find a scroll speed (px/frame) that divides tile_w evenly and produces
    a 3-5 second loop. Falls back to the nearest clean divisor."""
    target_min = 3
    target_max = 5
    min_speed = max(1, tile_w // (target_max * fps))
    max_speed = max(1, tile_w // (target_min * fps))

    for s in range(min_speed, max_speed + 1):
        if tile_w % s == 0:
            return s

    # Fallback: find nearest divisor that gives at least 1 second
    for s in range(1, tile_w + 1):
        if tile_w % s == 0:
            duration = tile_w / (s * fps)
            if duration >= 1:
                best = s
                if duration <= target_max:
                    return best
    return best


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a static image into a seamlessly looping scrolling GIF.",
    )
    parser.add_argument(
        "image",
        type=Path,
        help="path to the input image (PNG, JPG, BMP, etc.)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("scroll_gif.gif"),
        help="output GIF path (default: scroll_gif.gif)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=128,
        help="display width in pixels (default: 128)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=40,
        help="display height in pixels (default: 40)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=10,
        help="playback frame rate (default: 10)",
    )
    parser.add_argument(
        "--gap",
        type=int,
        default=40,
        help="black pixel gap between image repetitions (default: 40)",
    )
    parser.add_argument(
        "--speed",
        type=int,
        default=None,
        help="scroll speed in px/frame (auto-calculated if omitted)",
    )
    parser.add_argument(
        "--no-invert",
        action="store_true",
        help="skip color inversion (use if image is already white-on-black)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=128,
        help="black/white threshold 0-255 (default: 128)",
    )
    args = parser.parse_args()

    # Load and convert to grayscale
    img = Image.open(args.image).convert("L")

    # Threshold to pure black/white
    thresh = args.threshold
    img = img.point(lambda p: 255 if p > thresh else 0, mode="1")

    # Invert unless --no-invert (default: white image on black background)
    if not args.no_invert:
        img = img.point(lambda p: 0 if p else 1, mode="1")

    # Resize to display height, preserving aspect ratio
    aspect = img.width / img.height
    new_w = round(args.height * aspect)
    img = img.resize((new_w, args.height), Image.LANCZOS)

    # Build one tile: image + gap
    tile_w = new_w + args.gap
    tile = Image.new("1", (tile_w, args.height), 0)
    tile.paste(img, (0, 0))

    # Determine scroll speed
    scroll_speed = args.speed if args.speed else find_scroll_speed(tile_w, args.fps)

    # Ensure tile_w is divisible by scroll_speed for seamless looping
    if tile_w % scroll_speed != 0:
        # Pad tile width up to nearest multiple
        padded_w = tile_w + (scroll_speed - tile_w % scroll_speed)
        new_tile = Image.new("1", (padded_w, args.height), 0)
        new_tile.paste(tile, (0, 0))
        tile = new_tile
        tile_w = padded_w

    num_frames = tile_w // scroll_speed
    frame_duration_ms = 1000 // args.fps
    loop_duration = num_frames / args.fps

    print(f"Image width: {new_w}px, tile width: {tile_w}px")
    print(f"Scroll speed: {scroll_speed}px/frame, frames: {num_frames}, loop: {loop_duration:.1f}s")

    # Build a strip of 2 tiles for seamless cropping
    strip = Image.new("1", (tile_w * 2, args.height), 0)
    strip.paste(tile, (0, 0))
    strip.paste(tile, (tile_w, 0))

    # Generate frames — crop shifts right each frame, content moves left
    frames = []
    for i in range(num_frames):
        x = (i * scroll_speed) % tile_w
        frame = strip.crop((x, 0, x + args.width, args.height))
        frames.append(frame.convert("P"))

    # Save GIF
    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration_ms,
        loop=0,
    )

    print(f"Saved: {args.output} ({num_frames} frames, {args.width}x{args.height}, {args.fps} FPS)")


if __name__ == "__main__":
    main()
