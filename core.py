"""
SecureSteg — core.py
Chaotic-map key generation, LSB steganography (encode/decode),
PSNR, steganalysis, histogram, and bit-plane math.
Pure logic — no UI code here.
"""

import math
import numpy as np

END_MARKER = '\x00\x01\x02'


# =====================================================
# Chaotic key generation (mirrors the JS implementation)
# =====================================================

def normalize_seed(seed: float) -> float:
    s = abs(seed)
    if s == 0:
        s = 0.0001
    ip = math.floor(s)
    fp = s - ip
    x = ((ip * 0.6180339887) + fp + 0.1) % 1
    if x <= 0.0005 or x >= 0.9995 or abs(x - 0.5) < 0.0005:
        x = ((s * 12.9898) % 1 + 0.137) % 1
    return x


def chaotic_sequence(seed: float, tech: str, n: int):
    vals = []
    sn = normalize_seed(seed)

    if tech == 'logistic':
        x = sn
        r = 3.99
        for _ in range(n):
            x = r * x * (1 - x)
            vals.append(x)

    elif tech == 'tent':
        x = sn
        u = 1.99
        for _ in range(n):
            x = u * x if x < 0.5 else u * (1 - x)
            if x < 1e-6:
                x = sn * 0.5 + 1e-4
            vals.append(x)

    else:  # sign
        x = sn
        for i in range(n):
            t = (x * 12.9898) + (i * 78.233) + (sn * 37.719)
            v = math.sin(t) * 43758.5453123
            v = v - math.floor(v)
            x = v
            vals.append(v)

    return vals


def generate_key(seed: float, tech: str) -> str:
    vals = chaotic_sequence(float(seed), tech, 64)
    return ''.join(format(min(255, int(math.floor(v * 256))), '02x') for v in vals)


def shuffle_indices(n: int, seed: float, tech: str):
    arr = list(range(n))
    vals = chaotic_sequence(float(seed), tech, n)
    for i in range(n - 1, 0, -1):
        j = min(int(math.floor(vals[i] * (i + 1))), i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def xor_crypt(text: str, key: str) -> str:
    klen = len(key)
    out = []
    for i, ch in enumerate(text):
        start = (i * 2) % klen
        kb = int(key[start:start + 2], 16)
        out.append(chr(ord(ch) ^ kb))
    return ''.join(out)


def text_to_bits(text: str):
    bits = []
    for ch in text:
        c = ord(ch)
        for b in range(7, -1, -1):
            bits.append((c >> b) & 1)
    return bits


def bits_to_text(bits):
    out = []
    i = 0
    n = len(bits)
    while i + 7 < n:
        byte = 0
        for b in range(8):
            byte = (byte << 1) | bits[i + b]
        out.append(chr(byte))
        i += 8
    return ''.join(out)


def key_strength(key: str):
    """Returns (percent, label) — like the JS strength meter."""
    unique = len(set(key))
    pct = round((unique / 16) * 100)
    if pct < 40:
        return pct, 'Weak'
    elif pct < 75:
        return pct, 'Moderate'
    return pct, 'Strong'


# =====================================================
# LSB steganography — encode / decode
# =====================================================

def capacity_chars(width: int, height: int) -> int:
    px = width * height
    return max(0, (px * 3 - 24) // 8)


def encode_message(arr: np.ndarray, seed, tech: str, message: str) -> np.ndarray:
    """arr: HxWx4 (or HxWx3) uint8 numpy array. Returns a new array with the message hidden."""
    h, w = arr.shape[0], arr.shape[1]
    total_px = w * h

    key = generate_key(seed, tech)
    payload = message + END_MARKER
    encrypted = xor_crypt(payload, key)
    bits = text_to_bits(encrypted)

    if len(bits) > total_px * 3:
        raise ValueError("Message too long for this image.")

    order = shuffle_indices(total_px, float(seed), tech)

    out = arr.copy()
    flat = out.reshape(-1, out.shape[-1])

    bit_idx = 0
    n_bits = len(bits)
    for idx in order:
        if bit_idx >= n_bits:
            break
        for ch in range(3):
            if bit_idx >= n_bits:
                break
            flat[idx, ch] = (int(flat[idx, ch]) & 0xFE) | bits[bit_idx]
            bit_idx += 1

    return out


def decode_message(arr: np.ndarray, seed, tech: str):
    """Returns the decoded message string, or None if decoding failed."""
    h, w = arr.shape[0], arr.shape[1]
    total_px = w * h

    key = generate_key(seed, tech)
    order = np.array(shuffle_indices(total_px, float(seed), tech), dtype=np.int64)

    flat = arr.reshape(-1, arr.shape[-1])
    reordered = flat[order][:, :3]
    bits = (reordered & 1).astype(np.uint8).flatten()

    n = (len(bits) // 8) * 8
    bits = bits[:n].reshape(-1, 8)
    weights = np.array([128, 64, 32, 16, 8, 4, 2, 1], dtype=np.int64)
    byte_vals = (bits.astype(np.int64) * weights).sum(axis=1)
    raw = ''.join(chr(int(b)) for b in byte_vals)

    decrypted = xor_crypt(raw, key)
    end_idx = decrypted.find(END_MARKER)
    if end_idx == -1:
        return None
    return decrypted[:end_idx]


# =====================================================
# PSNR
# =====================================================

def calculate_psnr(arr_a: np.ndarray, arr_b: np.ndarray):
    if arr_a.shape[0] != arr_b.shape[0] or arr_a.shape[1] != arr_b.shape[1]:
        raise ValueError("Images must be the same dimensions.")

    a = arr_a[..., :3].astype(np.float64)
    b = arr_b[..., :3].astype(np.float64)

    diff = a - b
    mse = float(np.mean(diff ** 2))

    diff_mask = np.any(diff != 0, axis=-1)
    diff_px = int(np.sum(diff_mask))
    total_px = arr_a.shape[0] * arr_a.shape[1]

    if mse == 0:
        psnr_val = math.inf
    else:
        psnr_val = 10 * math.log10((255 * 255) / mse)

    pct = (diff_px / total_px) * 100

    if psnr_val == math.inf:
        verdict = "Images are bit-for-bit identical — no modification detected."
    elif psnr_val >= 50:
        verdict = "Excellent — change is invisible to any human observer. LSB steganography working perfectly."
    elif psnr_val >= 40:
        verdict = "Good — visually indistinguishable, but statistical tools could detect a difference."
    elif psnr_val >= 30:
        verdict = "Moderate — minor artifacts may appear under close inspection."
    else:
        verdict = "Poor — changes may be visible. Review encoding settings."

    return {
        'psnr': psnr_val,
        'mse': mse,
        'diff_px': diff_px,
        'pct': pct,
        'verdict': verdict,
    }


# =====================================================
# Histogram
# =====================================================

def build_histogram(arr: np.ndarray, channel: str):
    offset = {'r': 0, 'g': 1, 'b': 2}[channel]
    vals = arr[..., offset].astype(np.uint8)
    hist, _ = np.histogram(vals, bins=256, range=(0, 256))
    return hist


# =====================================================
# Steganalysis
# =====================================================

def analyze_steg(arr: np.ndarray):
    d = arr[..., :3].astype(np.int64)
    n = d.shape[0] * d.shape[1]
    total = n * 3

    flat = d.reshape(-1, 3).flatten()

    ones = int(np.sum(flat & 1))
    lsb_ratio = ones / total

    even_mask = (flat % 2 == 0)
    even_vals = (flat[even_mask] // 2)
    odd_vals = ((flat[~even_mask] - 1) // 2)

    freq_even = np.bincount(even_vals, minlength=128)[:128].astype(np.float64)
    freq_odd = np.bincount(odd_vals, minlength=128)[:128].astype(np.float64) if len(odd_vals) else np.zeros(128)

    chi_sq = 0.0
    pair_count = 0
    pairs = 0
    for i in range(128):
        observed = freq_odd[i]
        expected = (freq_odd[i] + freq_even[i]) / 2
        if expected > 0:
            chi_sq += ((observed - expected) ** 2) / expected
            pair_count += 1
        if abs(freq_odd[i] - freq_even[i]) < (freq_odd[i] + freq_even[i]) * 0.05:
            pairs += 1

    chi_avg = (chi_sq / pair_count) if pair_count else 0
    chi_norm = min(1, chi_avg / 50)
    pair_match = (pairs / 128 * 100)

    p = lsb_ratio
    entropy = -(p * math.log2(p) + (1 - p) * math.log2(1 - p)) if 0 < p < 1 else 0

    suspicion = 0
    suspicion += 40 if abs(lsb_ratio - 0.5) < 0.03 else (20 if abs(lsb_ratio - 0.5) < 0.06 else 0)
    suspicion += 30 if chi_norm > 0.7 else (15 if chi_norm > 0.4 else 0)
    suspicion += 20 if entropy > 0.95 else (10 if entropy > 0.85 else 0)
    suspicion += 10 if pair_match > 70 else 0
    suspicion = min(100, suspicion)

    if suspicion < 30:
        verdict = "\u2713 No steganographic content detected — LSB patterns appear natural."
        vclass = 'clean'
    elif suspicion < 65:
        verdict = "\u26a0 Possible hidden data — LSB distribution shows mild statistical anomalies."
        vclass = 'suspect'
    else:
        verdict = "\u2717 Hidden data likely present — LSB patterns are highly irregular."
        vclass = 'likely'

    return {
        'verdict': verdict,
        'vclass': vclass,
        'chi': chi_avg,
        'lsb_ratio': lsb_ratio * 100,
        'entropy': entropy,
        'pair_match': pair_match,
        'suspicion': suspicion,
    }


# =====================================================
# Bit planes
# =====================================================

def bitplane_gray(arr: np.ndarray, channel: str, plane: int) -> np.ndarray:
    offset = {'r': 0, 'g': 1, 'b': 2}[channel]
    vals = (arr[..., offset].astype(np.uint8) >> plane) & 1
    return (vals * 255).astype(np.uint8)
