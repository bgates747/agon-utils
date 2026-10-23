"""Independent byte-level plain-buffer contracts and legacy writer parity."""
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

API = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API))
import buffers
from riff import make_chunk


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PlainBuffers(unittest.TestCase):
    def test_exact_layout_and_nonconsecutive_ids(self):
        payload = bytes((25,4,0,0,0,0))
        encoded = buffers.build_container([buffers.BufferRecord(4321,payload)])
        # Independent golden byte string: no helper from the writer.
        expected = (b'RIFF'+struct.pack('<I',68)+b'AGNB'
                    +b'VERS\2\0\0\0\0\3\0\0'
                    +b'LIST'+struct.pack('<I',44)+b'BUFR'
                    +b'BHDR\2\0\0\0\xe1\x10\0\0'
                    +b'RAWD\1\0\0\0\0\0\0\0'
                    +b'DATA\6\0\0\0'+payload+b'\0\0')
        self.assertEqual(encoded,expected)
        records=[buffers.BufferRecord(n,b'x') for n in (65534,0,17)]
        self.assertEqual(buffers.read_container(buffers.build_container(records)),records)

    def test_windows_block_limit_and_aggregate_larger_than_host_app_ram(self):
        records=[buffers.BufferRecord(i+40,bytes((i,))*size)
                 for i,size in enumerate((1,8191,8192,8193,65535,65536,160000,200000))]
        encoded=buffers.build_container(records)
        self.assertGreater(len(encoded),0x70000)
        self.assertEqual(buffers.read_container(encoded),records)

    def test_invalid_records_and_duplicate_ids(self):
        for id in (-1,65535,65536,True,'42'):
            with self.subTest(id=id), self.assertRaises(ValueError):
                buffers.build_container([buffers.BufferRecord(id,b'x')])
        for data in (b'',bytearray(b'x'),b'x'*(buffers.MAX_DATA+1)):
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                buffers.build_container([buffers.BufferRecord(1,data)])
        with self.assertRaises(ValueError):
            buffers.build_container([buffers.BufferRecord(1,b'a'),buffers.BufferRecord(1,b'b')])

    def test_reject_truncation_every_boundary(self):
        encoded=buffers.build_container([buffers.BufferRecord(4,b'abcdefg')])
        for size in range(len(encoded)):
            with self.subTest(size=size),self.assertRaises(ValueError):
                buffers.read_container(encoded[:size])
        with self.assertRaises(ValueError):buffers.read_container(encoded+b'\0')

    def test_reject_bad_headers_metadata_and_padding(self):
        encoded=buffers.build_container([buffers.BufferRecord(4,b'abcdefg')])
        mutations=[(0,b'NOPE'),(8,b'XXXX'),(12,b'LIST'),(20,b'\1'),(21,b'\2'),(22,b'\1'),
                   (32,b'FAIL'),(36,b'DATA'),(44,b'\xff\xff'),(46,b'\1'),
                   (48,b'IMAG'),(52,b'\2'),(56,b'\1'),(57,b'\1'),(60,b'NOPE'),
                   (64,b'\xff\xff\xff\xff'),(len(encoded)-1,b'\1')]
        for at,value in mutations:
            with self.subTest(at=at),self.assertRaises(ValueError):
                changed=bytearray(encoded);changed[at:at+len(value)]=value
                buffers.read_container(bytes(changed))

    def test_repeated_ids_explicitly_replace_but_writer_rejects_them(self):
        single=buffers.build_container([buffers.BufferRecord(2,b'x')])
        duplicate=single+single[24:]
        duplicate=duplicate[:4]+struct.pack('<I',len(duplicate)-8)+duplicate[8:]
        self.assertEqual([r.buffer_id for r in buffers.read_container(duplicate)],[2,2])

    def test_manifest_paths_are_only_build_inputs_and_failure_preserves_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'source.bin').write_bytes(b'\0\1\2')
            manifest=root/'input.json';manifest.write_text(json.dumps({'records':[{'buffer_id':88,'path':'source.bin'}]}))
            output=root/'out.agnb';buffers.write_manifest(manifest,output)
            self.assertNotIn(b'source.bin',output.read_bytes())
            self.assertEqual(buffers.read_container(output.read_bytes()),[buffers.BufferRecord(88,b'\0\1\2')])
            before=output.read_bytes()
            manifest.write_text(json.dumps({'records':[{'buffer_id':65535,'path':'source.bin'}]}))
            with self.assertRaises(ValueError):buffers.write_manifest(manifest,output)
            self.assertEqual(output.read_bytes(),before)

    def test_legacy_audio_bytes_unchanged(self):
        module=load('audio_writer',API.parent/'audio/scripts/build_audio_container.py')
        record=module.AudioRecord('test',321,22050,b'\0\x80\xff')
        actual=module.build_container([record])
        # Match the pre-existing framing algorithm independently.
        def old_chunk(kind,payload):return kind+struct.pack('<I',len(payload))+payload+bytes((-len(payload))%4)
        body=(b'AGNB'+old_chunk(b'VERS',b'\0\2')+old_chunk(b'LIST',b'BUFR'
              +old_chunk(b'BHDR',struct.pack('<H',321))+old_chunk(b'AUDI',struct.pack('<BH',9,22050))
              +old_chunk(b'DATA',record.pcm)))
        self.assertEqual(actual,b'RIFF'+struct.pack('<I',len(body))+body)

    def test_shared_chunk_padding(self):
        for size in range(12):
            payload=b'x'*size
            self.assertEqual(make_chunk(b'TEST',payload),b'TEST'+struct.pack('<I',size)+payload+bytes((-size)%4))
        with self.assertRaises(ValueError):make_chunk(b'BAD',b'x')


if __name__=='__main__':unittest.main()
