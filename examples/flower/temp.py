def parse_fixed_point(value_str):
    integer_accum = 0  # Accumulator for integer part
    fractional_accum = 0  # Accumulator for fractional part
    scale_factor = 1  # Scale for fractional digits
    is_negative = False  # Track if the number is negative

    # Check for negative sign at the beginning
    if value_str.startswith('-'):
        is_negative = True
        value_str = value_str[1:]  # Skip the minus sign for processing

    # Process integer part of the number
    def process_integer_part():
        nonlocal integer_accum
        for char in value_str:
            if char == '.':
                return value_str.index('.') + 1  # Return position after decimal
            if '0' <= char <= '9':
                digit = ord(char) - ord('0')
                integer_accum = integer_accum * 10 + digit
        return len(value_str)  # No decimal point, so return end position

    # Process fractional part of the number
    def process_fractional_part(start_index):
        nonlocal fractional_accum, scale_factor
        for char in value_str[start_index:]:
            if '0' <= char <= '9':
                digit = ord(char) - ord('0')
                fractional_accum = fractional_accum * 10 + digit
                scale_factor *= 10
            else:
                break  # Stop processing at any non-numeric character

    # Execute the integer processing loop
    decimal_index = process_integer_part()

    # If there was a decimal point, execute the fractional processing loop
    if decimal_index < len(value_str):
        process_fractional_part(decimal_index)

    # Combine integer and fractional parts into a single fixed-point value
    # fixed_point_value = (integer_accum << 8) + (fractional_accum * (1 << 8) // scale_factor)
    fixed_point_value = integer_accum * 256 + fractional_accum * 256 // scale_factor
    # fixed_point_value = (integer_accum * 256) + (fractional_accum * 256 / scale_factor)


    # Apply negative sign if necessary
    if is_negative:
        fixed_point_value = -fixed_point_value & 0xFFFFFF  # Ensure it's in 24-bit format

    return f"{fixed_point_value:06X}"

# Example usage
value_str = "1.5"
result = parse_fixed_point(value_str)
print(f"Fixed-point representation of {value_str}: {result}")
