"""Generate placeholder PNG assets for Flutter app icon and splash screen."""
import struct, zlib, os

def make_png(w, h, r, g, b):
    """Create a minimal solid-color PNG."""
    def chunk(name, data):
        c = struct.pack('>I', len(data)) + name + data
        return c + struct.pack('>I', zlib.crc32(name + data) & 0xffffffff)
    
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    
    # Build raw image data
    raw = b''
    for _ in range(h):
        raw += b'\x00'  # filter none
        raw += bytes([r, g, b] * w)
    
    compressed = zlib.compress(raw, 9)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')
    return sig + ihdr + idat + iend

# ApnaGhar purple icon (1024x1024)
icon_path = os.path.join('apnaghar_app', 'assets', 'icon', 'app_icon.png')
with open(icon_path, 'wb') as f:
    f.write(make_png(1024, 1024, 13, 8, 32))  # #0d0820 deep purple
print(f"Created: {icon_path}")

# Splash screen (1242x2436 — iPhone max)
splash_path = os.path.join('apnaghar_app', 'assets', 'splash', 'splash.png')
with open(splash_path, 'wb') as f:
    f.write(make_png(1242, 2436, 13, 8, 32))  # #0d0820
print(f"Created: {splash_path}")

print("Assets ready!")
