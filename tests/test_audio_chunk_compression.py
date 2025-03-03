#!/usr/bin/env python3
import os
import subprocess
import math

# ----- Configuration -----
source_file = '/home/smith/Agon/mystuff/AgonJukebox/tgt/music/Singles/Barracuda.wav'
full_compressed_file = source_file + '.szip'
tmp_chunk_file = 'tmp_chunk.raw'
tmp_compressed_file = 'tmp_chunk.szip'
wav_header_size = 44  # Standard WAV header size; adjust if needed

# ----- Full File Compression -----
print("Compressing full file...")
subprocess.run(['szip', '-b41o3', source_file, full_compressed_file], check=True)
full_size = os.path.getsize(full_compressed_file)
print(f"Full file compressed size: {full_size} bytes")

# ----- Get Audio Info via ffprobe -----
print("Reading audio info with ffprobe...")
ffprobe_cmd = [
    "ffprobe", "-v", "error", "-select_streams", "a:0",
    "-show_entries", "stream=sample_rate,channels,duration",
    "-of", "default=noprint_wrappers=1:nokey=1", source_file
]
result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
lines = result.stdout.strip().split('\n')
if len(lines) < 3:
    raise RuntimeError("Error reading audio info from ffprobe.")

sample_rate = int(lines[0])
channels = int(lines[1])
duration = float(lines[2])
print(f"Sample rate: {sample_rate} Hz, Channels: {channels}, Duration: {duration} s")

# ----- Calculate Chunk Size -----
# For 8-bit PCM, each sample is 1 byte, so total bytes per second:
bytes_per_second = sample_rate * channels
print(f"Bytes per second: {bytes_per_second}")

# ----- Read the Audio Data, Skipping the .wav Header -----
with open(source_file, 'rb') as f:
    f.read(wav_header_size)  # Skip the WAV header
    audio_data = f.read()  # Read the actual PCM data

# ----- Process the Audio Data in 1-Second Chunks -----
total_chunk_compressed = 0
num_chunks = math.ceil(len(audio_data) / bytes_per_second)
print(f"Number of 1-second chunks: {num_chunks}")

for i in range(num_chunks):
    start = i * bytes_per_second
    end = start + bytes_per_second
    chunk = audio_data[start:end]
    
    # Write the chunk to a temporary file
    with open(tmp_chunk_file, 'wb') as f_chunk:
        f_chunk.write(chunk)
    
    # Compress the chunk using szip with the correct syntax
    subprocess.run(['szip', '-b41o3', tmp_chunk_file, tmp_compressed_file], check=True)
    chunk_compressed_size = os.path.getsize(tmp_compressed_file)
    print(f"Chunk {i+1}: Original {len(chunk)} bytes, Compressed {chunk_compressed_size} bytes")
    total_chunk_compressed += chunk_compressed_size

    # Cleanup temporary compressed file
    os.remove(tmp_compressed_file)

print(f"Total compressed size (chunked): {total_chunk_compressed} bytes")
