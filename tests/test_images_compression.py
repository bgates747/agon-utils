#!/usr/bin/env python3
import os
import csv
import subprocess

# ----- Helper Functions -----

def get_file_size(path):
    return os.path.getsize(path)

def compress_with_simz(input_file):
    """Compress using simz, writing output to a temp file."""
    temp_file = "temp.simz"
    subprocess.run(["simz", "-c", input_file, temp_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size = os.path.getsize(temp_file)
    os.remove(temp_file)
    return size

def compress_with_szip_b41o3(input_file):
    """Compress using szip, writing output to a temp file."""
    temp_file = "temp.szip"
    subprocess.run(["szip", "-b41o3", input_file, temp_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size = os.path.getsize(temp_file)
    os.remove(temp_file)
    return size

def compress_with_szip_b41o0(input_file):
    """Compress using szip, writing output to a temp file."""
    temp_file = "temp.szip"
    subprocess.run(["szip", "-b41o0", input_file, temp_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size = os.path.getsize(temp_file)
    os.remove(temp_file)
    return size

def compress_with_tvc(input_file):
    """Compress using tvc compression, writing output to a temp file."""
    temp_file = "temp.tvc"
    subprocess.run(["tvc", "-c", input_file, temp_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size = os.path.getsize(temp_file)
    os.remove(temp_file)
    return size

def compress_with_rle2(input_file):
    """Compress using rlecompress, writing output to a temp file."""
    temp_file = "temp.rle2"
    subprocess.run(["rle2", "-c", input_file, temp_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size = os.path.getsize(temp_file)
    os.remove(temp_file)
    return size

def compress_with_srle2(input_file):
    """Compress using rlecompress and szip, writing output to a temp file."""
    rle2_file = "temp.rle2"
    srle2_file = "temp.srle2"
    subprocess.run(["rle2", "-c", input_file, rle2_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["szip", "-b41o3", rle2_file, srle2_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size = os.path.getsize(srle2_file)
    os.remove(rle2_file)
    os.remove(srle2_file)
    return size

def compress_with_mskz(input_file):
    """Compress using mskz, writing output to a temp file."""
    temp_file = "temp.mskz"
    subprocess.run(["mskz", "-c", input_file, temp_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size = os.path.getsize(temp_file)
    os.remove(temp_file)
    return size

def compress_with_snappy(input_file):
    """Compress using snappy, writing output to a temp file."""
    temp_file = "temp.snpz"
    subprocess.run(["scmd", "-c", input_file, temp_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    size = os.path.getsize(temp_file)
    os.remove(temp_file)
    return size

# ----- Main Testing Function -----
def main():
    # Open CSV file for writing the report.
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write the header row.
        writer.writerow([
            "File", "Original",
            "Simz", "Szip_b41o3", "Szip_b41o0",
            "Tvc", "Rle2", "Srle2", "Mskz", "Snappy"
        ])

        for file in base_files:
            # Get absolute path for safety.
            file_path = os.path.abspath(file)
            file_path = os.path.splitext(file_path)[0] + f"_{palette_conversion_method}.rgba2"
            original_size = get_file_size(file_path)
            
            # Run each compression method.
            size_simz = compress_with_simz(file_path)
            size_szip_b41o3 = compress_with_szip_b41o3(file_path)
            size_szip_b41o0 = compress_with_szip_b41o0(file_path)
            size_tvc = compress_with_tvc(file_path)
            size_rle2 = compress_with_rle2(file_path)
            size_srle2 = compress_with_srle2(file_path)
            size_mskz = compress_with_mskz(file_path)
            size_snappy = compress_with_snappy(file_path)
            
            # Write results into the CSV.
            writer.writerow([
                os.path.basename(file),
                original_size,
                size_simz,
                size_szip_b41o3,
                size_szip_b41o0,
                size_tvc,
                size_rle2,
                size_srle2,
                size_mskz,
                size_snappy
            ])

if __name__ == '__main__':
    palette_conversion_method = 'bayer'
    transparent_color = (0, 0, 0, 0)  # Alpha 0 means NO transparent color
    palette_file = '/home/smith/Agon/mystuff/agon-utils/examples/palettes/Agon64.gpl'
    csv_file = f'tests/images/report_{palette_conversion_method}.csv'

    base_files = [
        'tests/images/rainbow_240x180.png',
        'tests/images/rainbow_320x240.png',
        'tests/images/rainbow_512x384.png',
        'tests/images/rainbow_640x480.png'
    ]

    main()
