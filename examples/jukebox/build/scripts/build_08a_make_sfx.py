import os
import sqlite3
import shutil
import subprocess
from tempfile import NamedTemporaryFile

def make_tbl_08_sfx(conn, cursor):
    """Create the database table for sound effects."""
    cursor.execute("DROP TABLE IF EXISTS tbl_08_sfx;")
    conn.commit()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_08_sfx (
            sfx_id INTEGER,
            size INTEGER,
            duration INTEGER,
            filename TEXT,
            PRIMARY KEY (sfx_id)
        );
    """)
    conn.commit()

def copy_to_temp(file_path):
    """Copy a file to a temporary file."""
    temp_file = NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_path)[1])
    shutil.copy(file_path, temp_file.name)
    return temp_file.name

def make_sfx(db_path, src_dir, tgt_dir, proc_dir, sample_rate):
    """
    Create 8-bit PCM SFX from .wav or .mp3 files, with the final step always
    being conversion to headerless 8-bit signed PCM. Demonstrates how to denoise
    post–8-bit-conversion by temporarily flipping back and forth between
    WAV and 8-bit raw.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    make_tbl_08_sfx(conn, cursor)

    # Create target and processed directories
    for directory in (tgt_dir, proc_dir):
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    sfxs = []
    for filename in sorted(os.listdir(src_dir)):
        if filename.endswith(('.wav', '.mp3')):
            filename_raw = os.path.splitext(filename)[0] + '.raw'
            sfxs.append((len(sfxs), filename, filename_raw))

    for sfx in sfxs:
        sfx_id, original_filename, raw_filename = sfx
        src_path = os.path.join(src_dir, original_filename)   # Original source file
        tgt_path = os.path.join(tgt_dir, raw_filename)        # Final .raw target file
        proc_path = os.path.join(
            proc_dir,
            os.path.splitext(original_filename)[0] + '.wav'
        )  # Intermediate WAV file for resampling, denoising, etc.

        # Convert to .wav if necessary
        if original_filename.endswith('.mp3'):
            temp_path = copy_to_temp(src_path)
            subprocess.run([
                'ffmpeg',
                '-y',              # Overwrite output file
                '-i', temp_path,   # Input file
                '-ac', '1',        # Set audio channels to mono
                proc_path          # Output file (WAV)
            ], check=True)
            os.remove(temp_path)
        else:
            shutil.copy(src_path, proc_path)

        # Resample the WAV to the target sample rate
        temp_path = copy_to_temp(proc_path)
        subprocess.run([
            'ffmpeg',
            '-y',                           # Overwrite output file
            '-i', temp_path,                # Input file
            '-ac', '1',                     # Mono
            '-ar', f'{sample_rate}',        # Resample rate in Hz
            proc_path                       # Output file (WAV)
        ], check=True)
        os.remove(temp_path)

        #
        # --- DENOISING IN THE 8-BIT DOMAIN ---
        #
        # Step 3: Convert the WAV to temporary 8-bit raw
        raw_8bit_temp = os.path.join(
            proc_dir,
            os.path.splitext(original_filename)[0] + '_temp8.raw'
        )
        temp_path = copy_to_temp(proc_path)
        subprocess.run([
            'ffmpeg',
            '-y',
            '-i', temp_path,                # Input (WAV)
            '-ac', '1',                     # Mono
            '-f', 's8',                     # Format: signed 8-bit PCM
            '-acodec', 'pcm_s8',            # Codec: PCM signed 8-bit
            raw_8bit_temp
        ], check=True)
        os.remove(temp_path)

        # Step 4: Denoise that 8-bit raw, converting it back to WAV
        temp_path = copy_to_temp(raw_8bit_temp)
        subprocess.run([
            'ffmpeg',
            '-y',
            '-f', 's8',                     # Input is raw 8-bit
            '-ar', f'{sample_rate}',        # Sample rate
            '-ac', '1',                     # Mono
            '-i', temp_path,                # Input file
            '-af', 'afftdn',                # Denoising filter (example)
            proc_path                        # Overwrite proc_path with a denoised WAV
        ], check=True)
        os.remove(temp_path)
        os.remove(raw_8bit_temp)

        #
        # --- FINAL STEP: Convert processed WAV to 8-bit RAW ---
        #
        temp_path = copy_to_temp(proc_path)
        subprocess.run([
            'ffmpeg',
            '-y',
            '-i', temp_path,                # Input (denoised WAV)
            '-ac', '1',                     # Mono
            '-f', 's8',                     # Format: signed 8-bit PCM
            '-acodec', 'pcm_s8',            # Codec: PCM signed 8-bit
            tgt_path                         # Final .raw output
        ], check=True)
        os.remove(temp_path)

        # Calculate size and duration
        size = os.path.getsize(tgt_path)
        duration = size // (sample_rate / 1000)  # milliseconds for 8-bit mono PCM
        cursor.execute("""
            INSERT INTO tbl_08_sfx (sfx_id, size, duration, filename)
            VALUES (?, ?, ?, ?);""", (sfx_id, size, duration, raw_filename))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    # sample_rate = 44100 # standard high quality audio
    sample_rate = 16384 # default rate for Agon
    # sample_rate = 15360/4 # for 8-bit PCM this is 256 bytes per 1/60th of a second
    db_path = 'build/data/build.db'
    src_dir = 'assets/sound/music/trimmed'
    proc_dir = 'assets/sound/music/processed'
    tgt_dir = 'tgt/music'

    make_sfx(db_path, src_dir, tgt_dir, proc_dir, sample_rate)
