import subprocess
import os
import tempfile
import zlib

def get_file_size(path):
    return os.path.getsize(path)

def compress_with_simz(input_file):
    """Compress using ./simz, writing output to a temp file."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_name = tmp.name
    try:
        subprocess.run(["./simz", "-c", input_file, tmp_name], check=True)
        compressed_size = os.path.getsize(tmp_name)
    finally:
        os.remove(tmp_name)
    return compressed_size

def compress_with_gzip(input_file):
    """Compress using gzip and capture output size."""
    result = subprocess.run(["gzip", "-c", input_file], check=True, stdout=subprocess.PIPE)
    return len(result.stdout)

def compress_with_zlib(input_file):
    """Compress using Python’s built-in zlib (same algorithm as minizip)."""
    with open(input_file, "rb") as f:
        data = f.read()
    compressed_data = zlib.compress(data, level=9)
    return len(compressed_data)

# def compress_with_7zip(input_file):
#     """Compress using 7zip, writing to a temp file."""
#     with tempfile.NamedTemporaryFile(delete=False) as tmp:
#         tmp_name = tmp.name
#     try:
#         subprocess.run(["7z", "a", "-bso0", "-bse0", tmp_name, input_file], check=True)
#         compressed_size = os.path.getsize(tmp_name)
#     finally:
#         os.remove(tmp_name)
#     return compressed_size

# def compress_with_zip(input_file):
#     """Compress using standard ZIP format, writing to a temp file."""
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
#         tmp_name = tmp.name
#     try:
#         subprocess.run(["zip", "-q", tmp_name, input_file], check=True)
#         compressed_size = os.path.getsize(tmp_name)
#     finally:
#         os.remove(tmp_name)
#     return compressed_size

def main():
    input_file = "frame_00005.rgba2"
    original_size = get_file_size(input_file)

    simz_size = compress_with_simz(input_file)
    gzip_size = compress_with_gzip(input_file)
    zlib_size = compress_with_zlib(input_file)
    # seven_zip_size = compress_with_7zip(input_file)
    # zip_size = compress_with_zip(input_file)

    print(f"Original file size: {original_size} bytes")
    print(f"Compressed with simz: {simz_size} bytes ({simz_size / original_size:.2%})")
    print(f"Compressed with gzip: {gzip_size} bytes ({gzip_size / original_size:.2%})")
    print(f"Compressed with zlib: {zlib_size} bytes ({zlib_size / original_size:.2%})")
    # print(f"Compressed with 7zip: {seven_zip_size} bytes ({seven_zip_size / original_size:.2%})")
    # print(f"Compressed with zip: {zip_size} bytes ({zip_size / original_size:.2%})")

if __name__ == "__main__":
    main()
