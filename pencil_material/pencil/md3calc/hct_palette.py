import math
import json

# ============================================================
# Material Color Utilities - HCT + CorePalette in Python
# Ported from https://github.com/material-foundation/material-color-utilities
# ============================================================

def linearized(rgb_component):
    normalized = rgb_component / 255.0
    if normalized <= 0.040449936:
        return normalized / 12.92 * 100.0
    return math.pow((normalized + 0.055) / 1.055, 2.4) * 100.0

def delinearized(rgb_component):
    normalized = rgb_component / 100.0
    if normalized <= 0.0031308:
        return normalized * 12.92 * 255.0
    return (1.055 * math.pow(normalized, 1.0 / 2.4) - 0.055) * 255.0

def clamp_int(min_val, max_val, val):
    return max(min_val, min(max_val, val))

def argb_from_rgb(r, g, b):
    return ((255 << 24) | ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)) & 0xFFFFFFFF

def red_from_argb(argb):
    return (argb >> 16) & 0xFF

def green_from_argb(argb):
    return (argb >> 8) & 0xFF

def blue_from_argb(argb):
    return argb & 0xFF

def argb_to_hex(argb):
    r = red_from_argb(argb)
    g = green_from_argb(argb)
    b = blue_from_argb(argb)
    return f"{r:02X}{g:02X}{b:02X}"

def xyz_from_argb(argb):
    r = linearized(red_from_argb(argb))
    g = linearized(green_from_argb(argb))
    b = linearized(blue_from_argb(argb))
    return [
        0.41233895 * r + 0.35762064 * g + 0.18051042 * b,
        0.2126 * r + 0.7152 * g + 0.0722 * b,
        0.01932141 * r + 0.11916382 * g + 0.95034478 * b,
    ]

def argb_from_xyz(x, y, z):
    linear_r =  3.2413774 * x - 1.5376545 * y - 0.4986162 * z
    linear_g = -0.9691729 * x + 1.8760109 * y + 0.0415561 * z
    linear_b =  0.0559453 * x - 0.2039588 * y + 1.0570641 * z
    r = clamp_int(0, 255, round(delinearized(linear_r)))
    g = clamp_int(0, 255, round(delinearized(linear_g)))
    b = clamp_int(0, 255, round(delinearized(linear_b)))
    return argb_from_rgb(r, g, b)

def _lab_f(t):
    e = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    if t > e:
        return math.pow(t, 1.0 / 3.0)
    return (kappa * t + 16.0) / 116.0

def lab_from_argb(argb):
    xyz = xyz_from_argb(argb)
    white_point = [95.047, 100.0, 108.883]
    fx = _lab_f(xyz[0] / white_point[0])
    fy = _lab_f(xyz[1] / white_point[1])
    fz = _lab_f(xyz[2] / white_point[2])
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return [L, a, b]

def argb_from_lstar(lstar):
    y = _y_from_lstar(lstar)
    component = delinearized(y)
    comp = round(component)
    comp = clamp_int(0, 255, comp)
    return argb_from_rgb(comp, comp, comp)

def _y_from_lstar(lstar):
    return 100.0 * _lab_inv_f((lstar + 16.0) / 116.0)

def _lab_inv_f(ft):
    e = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    ft3 = ft * ft * ft
    if ft3 > e:
        return ft3
    return (116.0 * ft - 16.0) / kappa

_WHITE_POINT_D65 = [95.047, 100.0, 108.883]

def _make_viewing_conditions():
    white_point = _WHITE_POINT_D65
    adapting_luminance = 200.0 / math.pi * _y_from_lstar(50.0) / 100.0
    background_lstar = 50.0
    rW = white_point[0] * 0.401288 + white_point[1] * 0.650173 + white_point[2] * -0.051461
    gW = white_point[0] * -0.250268 + white_point[1] * 1.204414 + white_point[2] * 0.045854
    bW = white_point[0] * -0.002079 + white_point[1] * 0.048952 + white_point[2] * 0.953227
    F, c, Nc = 1.0, 0.69, 1.0
    k = 1.0 / (5.0 * adapting_luminance + 1.0)
    k4 = k * k * k * k
    k4F = 1.0 - k4
    FL = k4 * adapting_luminance + 0.1 * k4F * k4F * math.pow(5.0 * adapting_luminance, 1.0 / 3.0)
    n = _y_from_lstar(background_lstar) / white_point[1]
    z = 1.48 + math.sqrt(50.0 * n)
    Nbb = 0.725 / math.pow(n, 0.2)
    Ncb = Nbb
    D = F * (1.0 - (1.0 / 3.6) * math.exp((-adapting_luminance - 42.0) / 92.0))
    D = max(0.0, min(1.0, D))
    rgbD = [
        D * (100.0 / rW) + 1.0 - D,
        D * (100.0 / gW) + 1.0 - D,
        D * (100.0 / bW) + 1.0 - D,
    ]
    rAW = math.pow(FL * rgbD[0] * rW / 100.0, 0.42)
    gAW = math.pow(FL * rgbD[1] * gW / 100.0, 0.42)
    bAW = math.pow(FL * rgbD[2] * bW / 100.0, 0.42)
    AW = (2.0 * rAW + gAW + 0.05 * bAW - 0.305) * Nbb
    return {
        'n': n, 'aw': AW, 'nbb': Nbb, 'ncb': Ncb, 'c': c, 'nc': Nc,
        'fl': FL, 'fl_root': math.pow(FL, 0.25), 'z': z,
        'rgb_d': rgbD, 'adapting_luminance': adapting_luminance,
    }

_DEFAULT_VC = _make_viewing_conditions()

def _cam16_from_xyz(x, y, z):
    vc = _DEFAULT_VC
    rgb_c = [
        x * 0.401288 + y * 0.650173 + z * -0.051461,
        x * -0.250268 + y * 1.204414 + z * 0.045854,
        x * -0.002079 + y * 0.048952 + z * 0.953227,
    ]
    rgb_d = [rgb_c[i] * vc['rgb_d'][i] for i in range(3)]

    def _adapt(c):
        af = math.pow(vc['fl'] * abs(c) / 100.0, 0.42)
        return (math.copysign(1, c) * 400.0 * af / (af + 27.13)) + 0.1

    rgb_a = [_adapt(c) for c in rgb_d]
    a = rgb_a[0] - 12.0 * rgb_a[1] / 11.0 + rgb_a[2] / 11.0
    b = (rgb_a[0] + rgb_a[1] - 2.0 * rgb_a[2]) / 9.0
    u = (20.0 * rgb_a[0] + 20.0 * rgb_a[1] + 21.0 * rgb_a[2]) / 20.0
    p2 = (40.0 * rgb_a[0] + 20.0 * rgb_a[1] + rgb_a[2]) / 20.0
    h = math.degrees(math.atan2(b, a)) % 360.0
    if h < 0:
        h += 360.0
    hPrime = h + 360.0 if h < 20.14 else h
    eHue = 0.25 * (math.cos(math.radians(hPrime) + 2.0) + 3.8)
    t = (50000.0 / 13.0 * vc['nc'] * vc['ncb'] * eHue * math.sqrt(a * a + b * b)) / (u + 0.305)
    alpha = math.pow(t, 0.9) * math.pow(1.64 - math.pow(0.29, vc['n']), 0.73)
    A = p2 * vc['nbb']
    J = 100.0 * math.pow(A / vc['aw'], vc['c'] * vc['z'])
    C = alpha * math.sqrt(J / 100.0)
    return {'hue': h, 'chroma': C, 'J': J, 'p2': p2, 'a': a, 'b': b}

def hct_from_argb(argb):
    xyz = xyz_from_argb(argb)
    cam = _cam16_from_xyz(xyz[0], xyz[1], xyz[2])
    lab = lab_from_argb(argb)
    return {'hue': cam['hue'], 'chroma': cam['chroma'], 'tone': lab[0]}

def _cam16_to_xyz(hue_radians, chroma, J):
    vc = _DEFAULT_VC
    if J <= 0 or chroma <= 0:
        return None
    alpha = chroma / math.sqrt(J / 100.0)
    t = math.pow(alpha / math.pow(1.64 - math.pow(0.29, vc['n']), 0.73), 1.0 / 0.9)
    h_deg = math.degrees(hue_radians) % 360.0
    eHue = 0.25 * (math.cos(math.radians(h_deg) + 2.0) + 3.8)
    Ac = vc['aw'] * math.pow(J / 100.0, 1.0 / (vc['c'] * vc['z']))
    p1 = 50000.0 / 13.0 * vc['nc'] * vc['ncb'] * eHue
    p2 = Ac / vc['nbb']
    h_sin = math.sin(hue_radians)
    h_cos = math.cos(hue_radians)
    if t == 0:
        gamma = 0
    else:
        gamma = (23.0 * (p2 + 0.305) * t) / (23.0 * p1 + 11.0 * t * h_cos + 108.0 * t * h_sin)
    a = gamma * h_cos
    b = gamma * h_sin
    rA = (460.0 * p2 + 451.0 * a + 288.0 * b) / 1403.0
    gA = (460.0 * p2 - 891.0 * a - 261.0 * b) / 1403.0
    bA = (460.0 * p2 - 220.0 * a - 6300.0 * b) / 1403.0

    def _inv_adapt(c):
        c_adj = c - 0.1
        abs_c = abs(c_adj)
        if (400.0 - abs_c) < 1e-10:
            return 0.0
        x = 27.13 * abs_c / (400.0 - abs_c)
        return math.copysign(1, c_adj) * 100.0 / vc['fl'] * math.pow(x, 1.0 / 0.42)

    rgb_c = [_inv_adapt(rA), _inv_adapt(gA), _inv_adapt(bA)]
    rgb = [rgb_c[i] / vc['rgb_d'][i] for i in range(3)]
    x = 1.86206786 * rgb[0] - 1.01125463 * rgb[1] + 0.14918677 * rgb[2]
    y = 0.38752654 * rgb[0] + 0.62144744 * rgb[1] - 0.00897398 * rgb[2]
    z = -0.01584150 * rgb[0] - 0.03412294 * rgb[1] + 1.04996444 * rgb[2]
    return [x, y, z]

def _solve_to_argb(hue, chroma, tone):
    if tone <= 0:
        return 0xFF000000
    if tone >= 100:
        return 0xFFFFFFFF
    if chroma < 1e-4:
        return argb_from_lstar(tone)
    hue_radians = math.radians(hue % 360.0)
    j_low, j_high = 0.0, 100.01
    best_argb = argb_from_lstar(tone)
    best_diff = 1e9
    for _ in range(20):
        j_mid = (j_low + j_high) / 2.0
        try:
            xyz = _cam16_to_xyz(hue_radians, chroma, j_mid)
            if xyz is None:
                j_low = j_mid
                continue
            argb = argb_from_xyz(xyz[0], xyz[1], xyz[2])
            lab = lab_from_argb(argb)
            actual_tone = lab[0]
            diff = abs(actual_tone - tone)
            if diff < best_diff:
                best_diff = diff
                best_argb = argb
            if diff < 0.002:
                break
            if actual_tone < tone:
                j_low = j_mid
            else:
                j_high = j_mid
        except Exception:
            j_low = j_mid
    return best_argb

class TonalPalette:
    def __init__(self, hue, chroma):
        self.hue = hue
        self.chroma = chroma
        self._cache = {}

    def tone(self, t):
        if t not in self._cache:
            self._cache[t] = _solve_to_argb(self.hue, self.chroma, t)
        return self._cache[t]

    def tone_hex(self, t):
        return "#" + argb_to_hex(self.tone(t))

class CorePalette:
    def __init__(self, argb):
        xyz = xyz_from_argb(argb)
        cam = _cam16_from_xyz(xyz[0], xyz[1], xyz[2])
        hue = cam['hue']
        chroma = cam['chroma']
        self.a1 = TonalPalette(hue, max(48.0, chroma))
        self.a2 = TonalPalette(hue, 16.0)
        self.a3 = TonalPalette(hue + 60.0, 24.0)
        self.n1 = TonalPalette(hue, 4.0)
        self.n2 = TonalPalette(hue, 8.0)
        self.error = TonalPalette(25.0, 84.0)

SEED_ARGB = 0xFFE91E63
TONES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100]

palette = CorePalette(SEED_ARGB)
seed_hct = hct_from_argb(SEED_ARGB)

palettes = {
    "primary":        palette.a1,
    "secondary":      palette.a2,
    "tertiary":       palette.a3,
    "neutral":        palette.n1,
    "neutralVariant": palette.n2,
    "error":          palette.error,
}

result = {
    "seedColor": "#E91E63",
    "hct": {
        "hue": round(seed_hct['hue'], 2),
        "chroma": round(seed_hct['chroma'], 2),
        "tone": round(seed_hct['tone'], 2),
    },
    "palettes": {}
}

for name, pal in palettes.items():
    result["palettes"][name] = {
        "hue": round(pal.hue, 2),
        "chroma": round(pal.chroma, 2),
        "tones": {}
    }
    for t in TONES:
        result["palettes"][name]["tones"][str(t)] = pal.tone_hex(t)

print(json.dumps(result, indent=2))
