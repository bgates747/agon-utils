
import re
import subprocess
import sqlite3
import numpy as np
import csv

def expand_lines(list_filename_in, list_filename_out):
    """Read input lines, expand multibyte lines, and write to the output file."""
    with open(list_filename_in, 'r') as infile, open(list_filename_out, 'w') as outfile:
        lines = infile.readlines()
        current_address = None  # Tracks the current address

        for line in lines:
            # Splitting the line based on fixed-width columns
            col1 = line[:7].strip()      # Address (7 chars)
            col2 = line[7:19].strip()    # Byte code (12 chars)
            col3_and_4 = line[19:].rstrip()  # Line number and source code (rest of the line)

            # Separate the line number and source code
            col3_split = col3_and_4.split(maxsplit=1)
            col3 = col3_split[0].strip().rjust(8) if col3_split else ""
            col4 = col3_split[1] if len(col3_split) > 1 else ""

            # Update the current address if available
            if col1:
                try:
                    current_address = int(col1, 16)
                except ValueError:
                    current_address = None

            # Expand byte code if present
            if col2:
                bytes_list = col2.split()

                # Write the first byte with source line details
                if current_address is not None:
                    outfile.write(f"{current_address:06X} {bytes_list[0]:<3} {col3} {col4}\n")
                    for byte in bytes_list[1:]:
                        current_address += 1
                        outfile.write(f"{current_address:06X} {byte:<3}\n")
                else:
                    outfile.write(f"{' ' * 7} {bytes_list[0]:<3} {col3} {col4}\n")
                    for byte in bytes_list[1:]:
                        outfile.write(f"{' ' * 7} {byte:<3}\n")
            else:
                # Handle lines without byte code
                if col3 or col4:
                    outfile.write(f"{' ' * 7} {' ' * 2} {col3} {col4}\n")
                else:
                    outfile.write(f"{' ' * 7}\n")

def make_dis_table(db_path, dif_filepath, table_name):
    """
    Creates a new table in the SQLite database from a dif file.
    The table will have an auto-incrementing idx field, an address as a unique primary key, 
    and fields for opcode and instruction text.

    Args:
        db_path (str): Path to the SQLite database file.
        dif_filepath (str): Path to the dif file to be imported.
        table_name (str): Name of the table to be created in the database.
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the table with idx (autoincremented), address, opcode, and instruction fields
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            idx INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE NOT NULL,
            opcode TEXT,
            instruction TEXT,
            matching TEXT
        )
    """)
    conn.commit()
    
    # Insert data from the dif file
    with open(dif_filepath, 'r') as dif_file:
        for line in dif_file:
            # Split line into components, assuming tab-separated address, opcode, and instruction
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue  # Skip lines that don't have address, opcode, and instruction
            
            address = parts[0].strip()
            opcode = parts[1].strip()
            instruction = parts[2].strip()
            matching = parts[3].strip() 

            # Insert data into the table, ignoring duplicates
            cursor.execute(f"""
                INSERT OR IGNORE INTO {table_name} (address, opcode, instruction, matching)
                VALUES (?, ?, ?, ?)
            """, (address, opcode, instruction, matching))

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f"Table '{table_name}' created and populated from {dif_filepath}")

def clean_disassembly_output(input_filepath, output_filepath):
    """Cleans up disassembly output by removing consecutive tabs and adding a normalized instruction with matching hex length."""
    with open(input_filepath, 'r') as infile:
        disassembly_lines = infile.readlines()

    output_lines = []
    for line in disassembly_lines:
        # Remove consecutive tabs
        line = re.sub(r'\t+', '\t', line)
        
        # Split line into parts by tabs
        parts = line.strip().split('\t')
        
        # Ensure there are at least three parts: address, opcode, and instruction
        if len(parts) < 3:
            output_lines.append(line.strip())
            continue

        # Extract the original instruction
        original_instruction = parts[2]

        # Normalize hex values in the instruction, preserving the length
        def normalize_hex(match):
            hex_string = match.group(0)  # Original hex string
            length = len(hex_string) - 1  # Exclude the "$" symbol
            return f"${'0' * length}"  # Keep the $ and replace with matching zeroes

        matching = re.sub(r'\$[0-9A-Fa-f]+', normalize_hex, original_instruction)

        # Add the normalized instruction to the end of the line
        output_line = f"{line.strip()}\t{matching}"
        output_lines.append(output_line)

    # Write the cleaned and extended output to the specified file
    with open(output_filepath, 'w') as outfile:
        outfile.write('\n'.join(output_lines) + '\n')

    print(f"Cleaned and normalized disassembly with added normalized instructions written to {output_filepath}")

def load_data_to_arrays(db_path, table_name):
    """Load normalized instructions and indexes into NumPy arrays."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT idx, matching FROM {table_name} ORDER BY idx")
    rows = cursor.fetchall()
    
    conn.close()
    
    # Extract indexes and normalized instructions into arrays
    idx_array = np.array([row[0] for row in rows], dtype=int)
    instruction_array = np.array([row[1] for row in rows], dtype=object)  # Use object type for strings
    return idx_array, instruction_array

def import_csv_to_table(db_path, csv_filepath, table_name):
    """Import a CSV file directly into a SQLite table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop and create the table for a fresh import
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            left_idx INTEGER,
            right_idx INTEGER
        )
    """)
    conn.commit()

    # Open the CSV file and insert data into the table
    with open(csv_filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        cursor.executemany(f"INSERT INTO {table_name} (left_idx, right_idx) VALUES (?, ?)", reader)

    conn.commit()
    conn.close()
    print(f"Data imported into table '{table_name}' from {csv_filepath}")

def import_fixed_width_to_db(db_path, lst_filepath, table_name):
    """Import data from a fixed-width .lst file into a SQLite table with an auto-incrementing primary key."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop the table if it exists and create a new one with `idx` as primary key
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            idx INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT,
            bytecode TEXT,
            linenum INTEGER,
            srccode TEXT,
            src_file TEXT
        )
    """)
    conn.commit()

    current_file = "no_file"  # Initial filename for lines preceding any matched pattern
    
    pattern = re.compile(r'; --- Begin (.+) ---')  # Pattern to match and extract filenames

    with open(lst_filepath, 'r') as lst_file:
        for line in lst_file:
            # Check for a new source file declaration
            match = pattern.search(line)
            if match:
                current_file = match.group(1).strip()
                continue  # Move to the next line after updating the filename

            # Parse fixed-width columns
            address = line[0:6].strip()
            bytecode = line[7:9].strip()
            linenum = line[10:19].strip()
            srccode = line[20:].strip()

            # Insert parsed data along with the current source file name into the database
            cursor.execute(f"""
                INSERT INTO {table_name} (address, bytecode, linenum, srccode, src_file)
                VALUES (?, ?, ?, ?, ?)
            """, (address, bytecode, linenum, srccode, current_file))

    conn.commit()
    conn.close()
    print(f"Data imported into table '{table_name}' from {lst_filepath}")

def create_final_table(db_path, final_table_name):
    """Create the final table with a primary key and schema matching the query output plus idx as primary key."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop the final table if it exists
    cursor.execute(f"DROP TABLE IF EXISTS {final_table_name}")
    # Create the final table with fields for both t1 (left-hand) and t2 (right-hand) data
    cursor.execute(f"""
        CREATE TABLE {final_table_name} (
            idx INTEGER PRIMARY KEY AUTOINCREMENT,
            idx1 INTEGER,
            address1 TEXT,
            opcode1 TEXT,
            instruction1 TEXT,
            matching1 TEXT,
            idx2 INTEGER,
            address2 TEXT,
            opcode2 TEXT,
            instruction2 TEXT,
            matching2 TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"Table '{final_table_name}' created.")
import sqlite3

def populate_final_table(db_path, final_table_name):
    """Populate the final table with query results without additional gap-filling logic."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute the query to retrieve data from `bbcbasic24` and `bbcbasic24ez` joined through `matched_indices`
    cursor.execute("""
        SELECT t1.idx1, t1.address1, t1.opcode1, t1.instruction1, t1.matching1,
               t2.idx2, t2.address2, t2.opcode2, t2.instruction2, t2.matching2
        FROM (
            SELECT t1.idx AS idx1, t1.address AS address1, t1.opcode AS opcode1, 
                   t1.instruction AS instruction1, t1.matching AS matching1 
            FROM bbcbasic24 AS t1
        ) AS t1
        JOIN matched_indices AS t3 ON t1.idx1 = t3.left_idx
        LEFT JOIN (
            SELECT t2.idx AS idx2, t2.address AS address2, t2.opcode AS opcode2, 
                   t2.instruction AS instruction2, t2.matching AS matching2 
            FROM bbcbasic24ez AS t2
        ) AS t2 ON t3.right_idx = t2.idx2
        ORDER BY t1.idx1
    """)
    
    # Fetch all results directly from the query
    results = cursor.fetchall()

    # Insert all fetched rows directly into the final table
    cursor.executemany(f"""
        INSERT INTO {final_table_name} (idx1, address1, opcode1, instruction1, matching1, idx2, address2, opcode2, instruction2, matching2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, results)

    conn.commit()
    conn.close()
    print(f"Data populated into table '{final_table_name}'.")

def generate_diff_from_arrays(idx_array1, instruction_array1, idx_array2, instruction_array2, diff_output_path, window_size, min_match_percentage):
    len1 = len(instruction_array1)
    matches = []
    i = 0  # Position in instruction_array1
    total_matches = 0
    max_consecutive_matches = 0
    unmatched_left = 0
    consecutive_matches = 0

    while i < len1:
        # Initialize variables to track the best matching window
        best_match_j = -1
        best_match_score = -1
        best_matches_mask = None
        len2 = len(instruction_array2)  # Update length of right array after any deletions

        # Adjust window size if we're near the end of the left array
        current_window_size = min(window_size, len1 - i)

        # Find the best matching window in instruction_array2 for the current window in instruction_array1
        for j in range(len2 - current_window_size + 1):
            # Ensure the first records in each window match exactly
            if not np.all(instruction_array1[i] == instruction_array2[j]):
                continue  # Skip to the next right-side window if the first records don't match

            # Compare the entire windows if the first records matched
            window_instr1 = instruction_array1[i:i + current_window_size]
            window_instr2 = instruction_array2[j:j + current_window_size]

            matches_mask = window_instr1 == window_instr2
            match_count = np.sum(matches_mask)
            match_percentage = (match_count / current_window_size) * 100

            if match_percentage > best_match_score:
                best_match_score = match_percentage
                best_match_j = j
                best_matches_mask = matches_mask

        # Proceed only if the best match percentage is greater than the threshold
        if best_match_score > min_match_percentage:
            j = best_match_j  # Start matching from the best-matching position in instruction_array2

            # Count consecutive matches
            consecutive_matches = 0
            while i < len1 and j < len(instruction_array2):
                instr1 = instruction_array1[i]
                instr2 = instruction_array2[j]

                if np.all(instr1 == instr2):  # Exact match
                    # Record the match and remove matched entries from the right-hand arrays
                    matches.append((idx_array1[i], idx_array2[j]))
                    idx_array2 = np.delete(idx_array2, j)
                    instruction_array2 = np.delete(instruction_array2, j)
                    consecutive_matches += 1
                    i += 1
                else:
                    break  # Stop matching on the first mismatch
            
            # Log successful match resolution
            print(f"Matched {consecutive_matches} records at left index {i}/{len1} on right index {j}/{len2} with score of {best_match_score:.2f}%.")
            max_consecutive_matches = max(max_consecutive_matches, consecutive_matches)
            total_matches += consecutive_matches
        else:
            # No sufficient match found, move to the next left index
            matches.append((idx_array1[i], None))  # No match on the right-hand side
            unmatched_left += 1
            i += 1

    # Handle any remaining lines in instruction_array1 with no matches
    trailing_unmatched_left = 0
    while i < len1:
        matches.append((idx_array1[i], None))
        unmatched_left += 1
        trailing_unmatched_left += 1
        i += 1

    # Append any remaining unmatched lines from instruction_array2
    unmatched_right = len(idx_array2)
    for idx in idx_array2:
        matches.append((None, idx))

    # Calculate and display summary
    total_left = len(idx_array1)
    total_right = len(instruction_array2)
    percent_matched = (total_matches / total_left) * 100 if total_left > 0 else 0
    avg_consecutive_matches = total_matches / (total_left - unmatched_left) if total_left > unmatched_left else 0

    print("\n--- Summary ---")
    print(f"Total matched records: {total_matches}")
    print(f"Total unmatched left-hand records: {unmatched_left}")
    print(f"Total trailing unmatched left-hand records inserted: {trailing_unmatched_left}")
    print(f"Total unmatched right-hand records inserted: {unmatched_right}")
    print(f"Percent total matched: {percent_matched:.2f}%")
    print(f"Average consecutive matches: {avg_consecutive_matches:.2f}")
    print(f"Max consecutive matches: {max_consecutive_matches}")

    # Write the matches to the output file
    with open(diff_output_path, 'w') as f:
        for left_idx, right_idx in matches:
            if right_idx is not None:
                f.write(f"{left_idx},{right_idx}\n")
            else:
                f.write(f"{left_idx},\n")  # No matching right index

    print(f"\nDiff generated and written to {diff_output_path}")

import sqlite3
import csv

def export_query_to_csv(db_path, output_csv_path):
    """Execute a query and save the results in CSV format with headers, outputting NULLs as empty fields."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Define the query with LEFT JOIN and ORDER BY clause
    query = """
        SELECT t1.idx, t1.idx1, t1.idx2, t1.address1, t1.address2, t1.opcode1, t1.opcode2,
        t1.instruction1, t1.instruction2, t1.matching1, t2.src_file, t2.srccode
        FROM final_table AS t1
        LEFT JOIN bbcbasic24ez_lst AS t2 ON t1.address2 = LOWER(t2.address)
        ORDER BY t1.idx
    """
    
    # Execute the query
    cursor.execute(query)
    # Fetch column names and query results
    column_names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    
    # Write to CSV file
    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Write headers
        csv_writer.writerow(column_names)
        
        # Write rows with None as empty fields for CSV null representation
        for row in rows:
            csv_writer.writerow([field if field is not None else '' for field in row])

    conn.close()
    print(f"Query results saved to '{output_csv_path}' in CSV format with NULLs as empty fields.")

def compare_binaries(left_hand_filepath, right_hand_filepath, src_base_filename):
    # Define the output file path
    cmp_output_filepath = f"{src_base_filename}_cmp.txt"
    
    # Construct the shell command
    cmp_command = (
        f"cmp -l {left_hand_filepath} {right_hand_filepath} "
        f"| gawk '{{printf \"%08X %02X %02X\\n\", $1-1, strtonum(0$2), strtonum(0$3)}}'"
    )
    
    # Run the command and redirect output to the desired file
    with open(cmp_output_filepath, 'w') as cmp_output_file:
        subprocess.run(cmp_command, shell=True, stdout=cmp_output_file, check=True)
    
    print(f"Comparison output written to {cmp_output_filepath}")

if __name__ == "__main__":
    db_path = 'utils/dif/difs.db'
    source_dir = 'src'
    tgt_bin_dir = 'utils/bin'
    dif_dir = 'utils/dif'

    list_filename_in = 'utils/dif/bbcbasic24ez.lst'
    list_filename_out = 'utils/dif/bbcbasic24ez_expanded.lst'
    if True: expand_lines(list_filename_in, list_filename_out)

    table_name = 'bbcbasic24ez_lst'
    # Import the .lst file into the SQLite table
    if True: import_fixed_width_to_db(db_path, list_filename_out, table_name)

    src_base_filename = 'bbcbasic24ez'
    src_filepath = f'{source_dir}/{src_base_filename}.asm'

    left_hand_filepath = f'{dif_dir}/bbcbasic24.dis.asm'
    right_hand_filepath = f'{dif_dir}/{src_base_filename}.dis.asm'

    compare_binaries(left_hand_filepath, right_hand_filepath, src_base_filename)

    ez80_dis_args = '--start 0 --target 0x040000 --address --hex-dump --lowercase --explicit-dest --ez80 --prefix --hex --mnemonic-space --no-argument-space --compute-absolute --literal-absolute'

    if True:
        # Now disassemble the generated binary
        cmd = f"ez80-dis {ez80_dis_args} orig/bbcbasic24.bin > {left_hand_filepath}"
        print (f"Running command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        clean_disassembly_output(left_hand_filepath, left_hand_filepath)
        print(f"Disassembly written to {left_hand_filepath}")
        make_dis_table(db_path, left_hand_filepath, 'bbcbasic24')

    if True:
        # Now disassemble the generated binary
        cmd = f"ez80-dis {ez80_dis_args} {tgt_bin_dir}/{src_base_filename}.bin > {right_hand_filepath}"
        print (f"Running command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        clean_disassembly_output(right_hand_filepath, right_hand_filepath)
        print(f"Disassembly written to {right_hand_filepath}")
        make_dis_table(db_path, right_hand_filepath, src_base_filename)

    # Generate the diff and write to the diff output file
    diff_output_path = f'{dif_dir}/{src_base_filename}.dif'

    # Main workflow
    left_table = 'bbcbasic24'
    right_table = src_base_filename
    
    # Set parameters
    window_size = 32
    step_size = window_size  # Or adjust as needed
    min_match_percentage = 80  # Adjust as needed

    if True:
        # Load data from the databases
        idx_array1, instruction_array1 = load_data_to_arrays(db_path, left_table)
        idx_array2, instruction_array2 = load_data_to_arrays(db_path, right_table)
        # Call the function
        generate_diff_from_arrays(idx_array1, instruction_array1, idx_array2, instruction_array2, diff_output_path, window_size, min_match_percentage)
    
    # Import the diff file into a table
    diff_table = 'matched_indices'
    if True: import_csv_to_table(db_path, diff_output_path, diff_table)

    # Create the final table
    final_table_name = 'final_table'
    if True: 
        create_final_table(db_path, final_table_name)
        populate_final_table(db_path, final_table_name)

    # Export the final query results to a CSV file
    output_csv_path = f'{dif_dir}/{src_base_filename}.csv'
    if True: export_query_to_csv(db_path, output_csv_path)
