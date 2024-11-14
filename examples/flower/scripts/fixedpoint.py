def compute_offset(n1, m1, n2, m2, n3, m3):
    # Validate that inputs and outputs are 24 bits total
    if n1 + m1 != 24 or n2 + m2 != 24 or n3 + m3 != 24:
        raise ValueError("Inputs and outputs must be 24 bits total.")

    # Total fractional bits in the product
    m_total = m1 + m2

    # Desired exponents for output format
    e_out_min = -m3

    # Calculate bit positions
    p_min = e_out_min + m_total

    # Compute the offset from LSB
    offset = p_min

    return int(offset)

# Example usage
if __name__ == "__main__":
    # Input precision
    m1 = 0
    m2 = 0
    # Output precision
    m3 = 1

    n1 = 24 - m1
    n2 = 24 - m2
    n3 = 24 - m3

    offset = compute_offset(n1, m1, n2, m2, n3, m3)
    print(f"Offset from LSB: {offset} bits")
