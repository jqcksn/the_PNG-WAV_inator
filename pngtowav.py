import numpy as np
from PIL import Image, PngImagePlugin
import math
import os
import struct
from scipy.io import wavfile

def write_custom_wav(wav_path, sample_rate, data, width=None):
    wavfile.write(wav_path, sample_rate, data)
    if width is not None:
        with open(wav_path, "r+b") as f:
            f.seek(0, os.SEEK_END)
            chunk_id = b"wdth"
            payload = struct.pack("<I", width)
            size = struct.pack("<I", len(payload))
            f.write(chunk_id + size + payload)

def read_custom_wav_width(wav_path):
    try:
        with open(wav_path, "rb") as f:
            content = f.read()
            pos = 12
            while pos + 8 <= len(content):
                chunk_id = content[pos:pos+4]
                size = struct.unpack("<I", content[pos+4:pos+8])[0]
                if chunk_id == b"wdth":
                    return struct.unpack("<I", content[pos+8:pos+12])[0]
                pos += 8 + size
    except:
        pass
    return None

def load_audio(audio_path):
    sr, data = wavfile.read(audio_path)
    if data.ndim > 1:
        data = data[:, 0]
    return sr, data.astype(np.int16)

def audio_to_rgb_png(audio_path, png_path, width=None):
    sr, data = load_audio(audio_path)
    byte_data = data.astype(np.int16).tobytes()
    total_bytes = len(byte_data)

    rgb_data = []
    for i in range(0, total_bytes, 3):
        r = byte_data[i]
        g = byte_data[i+1] if i+1 < total_bytes else 0
        b = byte_data[i+2] if i+2 < total_bytes else 0
        rgb_data.append((r % 256, g % 256, b % 256))
    rgb_data = np.array(rgb_data, dtype=np.uint8)

    if width is None:
        width = read_custom_wav_width(audio_path)
        if width is None:
            default_w = math.ceil(math.sqrt(len(rgb_data)))
            user_input = input(f"No width metadata found. Enter desired width (default {default_w}): ").strip()
            width = int(user_input) if user_input else default_w

    height = math.ceil(len(rgb_data) / width)
    pad_len = width * height - len(rgb_data)
    if pad_len > 0:
        rgb_data = np.vstack([rgb_data, np.zeros((pad_len,3), dtype=np.uint8)])

    img_array = rgb_data.reshape((height, width, 3))
    img = Image.fromarray(img_array, "RGB")

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("samplerate", str(sr))
    img.save(png_path, pnginfo=metadata)
    print(f"Saved RGB PNG: {png_path} ({width}x{height})")

def image_to_audio(image_path, wav_path):
    img = Image.open(image_path).convert("RGB")
    rgb_array = np.array(img)
    flat_rgb = rgb_array.reshape(-1,3)

    byte_list = []
    for pixel in flat_rgb:
        byte_list.extend(pixel.tolist())
    byte_data = bytes(byte_list)

    if len(byte_data) % 2 != 0:
        byte_data += b"\x00"
    samples = np.frombuffer(byte_data, dtype=np.int16)

    sr = img.info.get("samplerate")
    if sr is None:
        user_input = input("No sample rate metadata found. Enter sample rate (default 44100): ").strip()
        sr = int(user_input) if user_input else 44100
    else:
        sr = int(sr)
    write_custom_wav(wav_path, sr, samples, width=img.width)
    print(f"Saved WAV: {wav_path} ({len(samples)} samples at {sr} Hz)")


print("Choose operation:\n1 - WAV → Image\n2 - Image → WAV")

choice = -1
while choice != '1' and choice != '2':
    choice = input("Please enter 1 or 2: ").strip()

if choice == "1":
    audio_path = ''
    while not audio_path.endswith('.wav'):
        audio_path = input("Enter input WAV filename: ").strip()
    default_out = os.path.splitext(audio_path)[0] + "_png.png"
    png_path = ''
    while not png_path.endswith('.png'):
        png_path = input(f"Enter output PNG path (default: {default_out}): ").strip().strip('"')
        if not png_path:
            png_path = default_out
    audio_to_rgb_png(audio_path, png_path)

elif choice == "2":
    image_path = ''
    while not (image_path.endswith('.png') or image_path.endswith('.jpg')):
        image_path = input("Enter input image path (PNG or JPG): ").strip()
    default_out = os.path.splitext(image_path)[0] + "_wav.wav"
    wav_path = ''
    while not wav_path.endswith('.wav'):
        wav_path = input(f"Enter output WAV path (default: {default_out}): ").strip()
        if not wav_path:
            wav_path = default_out
    image_to_audio(image_path, wav_path)

else:
    print("Invalid choice. Exiting.")
