import agonutils

def test_hello():
    agonutils.hello()
    print("Hello function works!")


def test_simz_bytes_round_trip():
    original = bytes(range(256)) * 16
    encoded = agonutils.simz_encode_bytes(original)
    decoded = agonutils.simz_decode_bytes(encoded)
    assert decoded == original

if __name__ == '__main__':
    agonutils.hello()
    test_simz_bytes_round_trip()
