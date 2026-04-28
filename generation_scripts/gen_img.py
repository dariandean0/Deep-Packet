import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

def vigenere_encrypt(pt, key):
    key = key.upper()
    result, ki = [], 0
    for ch in pt.upper():
        if ch.isalpha():
            shift = ord(key[ki % len(key)]) - ord('A')
            result.append(chr((ord(ch) - ord('A') + shift) % 26 + ord('A')))
            ki += 1
        else:
            result.append(ch)
    return ''.join(result)

import os
KEY = os.environ.get("VIGENERE_KEY", "DEEPPACKET")
PLAINTEXT = os.environ.get("PLAINTEXT_SECRET", "HTTP://STAGE3:8003/")
ciphertext = vigenere_encrypt(PLAINTEXT, KEY)
payload = f"CIPHER:VIGENERE CIPHERTEXT:{ciphertext}"
print(f"Ciphertext : {ciphertext}")
print(f"Payload    : {payload}")

# Rebuild the same spectrogram image (same seed)
np.random.seed(10)
W, H = 512, 256
img = np.zeros((H, W, 3), dtype = np.uint8)
noise = np.random.randint(5, 25, (H, W), dtype = np.uint8)
img[:, :, 0] = noise // 2
img[:, :, 1] = noise // 3
img[:, :, 2] = noise
for _ in range(6):
    cy   = np.random.randint(20, H - 20)
    bw   = np.random.randint(3, 12)
    intn = np.random.randint(60, 180)
    col  = np.random.randint(0, 3)
    band = np.clip(np.random.randint(intn - 30, intn + 30, (bw * 2, W)), 0, 255).astype(np.uint8)
    y0, y1 = max(0, cy - bw), min(H, cy + bw)
    img[y0:y1, :, col] = band[:y1 - y0, :]
bx, by = np.random.randint(80, 420), np.random.randint(60, 190)
for dy in range(-8, 9):
    for dx in range(-40, 41):
        if 0 <= by+dy < H and 0 <= bx+dx < W:
            fade = max(0, 1.0 - abs(dx)/40.0) * max(0, 1.0 - abs(dy)/8.0)
            img[by+dy, bx+dx, 1] = min(255, int(img[by+dy, bx+dx, 1] + 200 * fade))
            img[by+dy, bx+dx, 2] = min(255, int(img[by+dy, bx+dx, 2] + 80  * fade))

# Embed payload in LSB of red channel
payload_bytes = payload.encode('ascii') + b'\x00'
bits = []
for byte in payload_bytes:
    for i in range(7, -1, -1):
        bits.append((byte >> i) & 1)
flat_r = img[:, :, 0].flatten().copy()
for i, bit in enumerate(bits):
    flat_r[i] = (flat_r[i] & 0xFE) | bit
img[:, :, 0] = flat_r.reshape(H, W)

# Save with updated Artist metadata
png_meta = PngInfo()
png_meta.add_text("Artist", KEY)
png_meta.add_text("Comment", "SIGINT capture - 03:47 UTC")
out_path = "/home/dariand/florida_tech/courses/cyber/projects/Deep-Packet/stages/stage2/files/signal.png"
Image.fromarray(img, 'RGB').save(out_path, pnginfo = png_meta)

# Verify
img_check = np.array(Image.open(out_path))
flat_r2 = img_check[:, :, 0].flatten()
recovered_bits = [flat_r2[i] & 1 for i in range(len(bits))]
recovered_bytes = bytearray()
for i in range(0, len(recovered_bits), 8):
    byte = 0
    for b in recovered_bits[i:i+8]:
        byte = (byte << 1) | b
    if byte == 0:
        break
    recovered_bytes.append(byte)
    
print(f"Verified   : {recovered_bytes.decode('ascii')}")
print(f"Artist tag : {Image.open(out_path).info.get('Artist')}")