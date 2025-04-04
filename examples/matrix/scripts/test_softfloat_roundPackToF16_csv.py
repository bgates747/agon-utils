#!/usr/bin/env python3
import os
import struct
import csv

def read_test_data_and_create_csv(bin_filename, csv_filename):
    """Read binary test data and output to CSV with all fields in hex format."""
    if not os.path.exists(bin_filename):
        print(f"Error: Binary file {bin_filename} not found.")
        return
    
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    
    with open(bin_filename, 'rb') as bin_file, open(csv_filename, 'w', newline='') as csv_file:
        # Create CSV writer and write header
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['sign', 'exp', 'sig', 'packed_p', 'sign_p', 'exp_p', 'mantissa_p','packed_a', 'sign_a', 'exp_a', 'mantissa_a'])
        
        # Read binary data in chunks - each record is 16 bytes
        while True:
            record_bytes = bin_file.read(16)  # 16 bytes per record
            if not record_bytes or len(record_bytes) < 16:
                break
            
            # Unpack the full record - 11 fields total
            # Format: <BBHHBBHHBBH for sign,exp,sig,packed_p,sign_p,exp_p,mantissa_p,packed_a,sign_a,exp_a,mantissa_a
            sign, exp, sig, packed_p, sign_p, exp_p, mantissa_p, packed_a, sign_a, exp_a, mantissa_a = struct.unpack('<BBHHBBHHBBH', record_bytes)
            
            # Write row to CSV with consistent hex formatting
            csv_writer.writerow([
                f"0x{sign:02x}", f"0x{exp:02x}", f"0x{sig:04x}",
                f"0x{packed_p:04x}", f"0x{sign_p:02x}", f"0x{exp_p:02x}", f"0x{mantissa_p:04x}",
                f"0x{packed_a:04x}", f"0x{sign_a:02x}", f"0x{exp_a:02x}", f"0x{mantissa_a:04x}"
            ])
    
    print(f"CSV file created: {csv_filename}")

# ----------------------------
# Main Function
# ----------------------------
if __name__ == "__main__":
    # Set parameters directly
    bin_file = 'tgt/softfloat_roundPackToF16.bin'
    csv_file = 'tgt/softfloat_roundPackToF16.csv'
    
    read_test_data_and_create_csv(bin_file, csv_file)