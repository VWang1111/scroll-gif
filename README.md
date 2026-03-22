# scroll-gif

Convert a static image into a seamlessly looping scrolling GIF animation.

Originally built for the OLED panel on the **SteelSeries Apex Pro** keyboard (128x40), but works for any use case that needs a scrolling black-and-white GIF — signage, badges, stream overlays, other keyboards, etc.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

No manual dependency installation needed — `uv run` handles it automatically.

## Quick start

```sh
uv run scroll_gif.py logo.png
```

This produces `scroll_gif.gif` — a 128x40 black-and-white animation at 10 FPS with seamless looping.

## CLI reference

| Argument | Default | Description |
|---|---|---|
| `image` | *(required)* | Path to input image (PNG, JPG, BMP, etc.) |
| `-o`, `--output` | `scroll_gif.gif` | Output GIF path |
| `--width` | `128` | Display width in pixels |
| `--height` | `40` | Display height in pixels |
| `--fps` | `10` | Playback frame rate |
| `--gap` | `40` | Black pixel gap between image repetitions |
| `--speed` | *auto* | Scroll speed in px/frame (auto-selects for a 3-5s loop) |
| `--no-invert` | off | Skip color inversion (for images already white-on-black) |
| `--threshold` | `128` | Black/white cutoff (0-255) |

## Examples

**SteelSeries Apex Pro (default settings):**

```sh
uv run scroll_gif.py my-logo.png
```

**Custom display size:**

```sh
uv run scroll_gif.py my-logo.png --width 256 --height 64
```

**Image already white-on-black:**

```sh
uv run scroll_gif.py white-on-black-logo.png --no-invert
```

**Faster scroll, custom output path:**

```sh
uv run scroll_gif.py my-logo.png --speed 6 -o fast-scroll.gif
```

## How it works

1. The input image is converted to grayscale, thresholded to pure black/white, and inverted (white graphic on black background — standard for OLED)
2. The image is resized to the display height while preserving aspect ratio
3. A "tile" is created by appending a configurable black gap after the image
4. The tile is repeated horizontally, and for each frame a display-sized window is cropped at an incrementing offset
5. Scroll speed is auto-calculated to produce a seamless loop lasting 3-5 seconds. A manual `--speed` override is available for fine-tuning
