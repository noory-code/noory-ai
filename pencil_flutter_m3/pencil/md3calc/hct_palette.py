"""
Material Design 3 HCT palette generator.
Uses materialyoucolor (official Python port of material-color-utilities).

Usage:
    python3 hct_palette.py <seed_hex>
    python3 hct_palette.py "#6750A4"
"""
import json
import sys

from materialyoucolor.hct import Hct
from materialyoucolor.palettes.core_palette import CorePalette

TONES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100]


def argb_to_hex(argb: int) -> str:
    r = (argb >> 16) & 0xFF
    g = (argb >> 8) & 0xFF
    b = argb & 0xFF
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_argb(hex_str: str) -> int:
    hex_str = hex_str.lstrip("#")
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return (0xFF << 24) | (r << 16) | (g << 8) | b


def palette_tones(tonal_palette) -> dict[str, str]:
    return {str(t): argb_to_hex(tonal_palette.tone(t)) for t in TONES}


def generate(seed_hex: str) -> dict:
    seed_argb = hex_to_argb(seed_hex)
    palette = CorePalette.of(seed_argb)
    seed_hct = Hct.from_int(seed_argb)

    return {
        "seedColor": seed_hex,
        "hct": {
            "hue": round(seed_hct.hue, 2),
            "chroma": round(seed_hct.chroma, 2),
            "tone": round(seed_hct.tone, 2),
        },
        "palettes": {
            "primary": palette_tones(palette.a1),
            "secondary": palette_tones(palette.a2),
            "tertiary": palette_tones(palette.a3),
            "neutral": palette_tones(palette.n1),
            "neutralVariant": palette_tones(palette.n2),
            "error": palette_tones(palette.error),
        },
    }


if __name__ == "__main__":
    seed = sys.argv[1] if len(sys.argv) > 1 else "#E91E63"
    print(json.dumps(generate(seed), indent=2))
