"""Explicit specification fixtures; not a production encoder or parser.
Run only to deliberately revise the frozen oracle files, never inside SUT tests.
"""
from pathlib import Path
import hashlib,json,zlib
ROOT=Path(__file__).resolve().parent

def crc_bitwise(data):
    value=0xffffffff
    for byte in data:
        value ^= byte
        for _ in range(8):
            value=(value>>1)^ (0xedb88320 if value & 1 else 0)
    return value ^ 0xffffffff

assert crc_bitwise(b'123456789')==0xcbf43926==zlib.crc32(b'123456789')
u16=lambda n:n.to_bytes(2,'little')
u32=lambda n:n.to_bytes(4,'little')
run=bytes.fromhex('000102030405060708090a0b0c0d0e0f')
# Manual field ordering and literal values, independently from any future implementation.
entry=bytes.fromhex('a5 5a 03 02 01 06 05 04 09 08 07 0c 0b 0a 0f 0e 0d 00 f0 0b 00 10 04 00 01 00 ff 03 00 00 00 00')
assert len(entry)==32 and entry[11:14]==bytes.fromhex('0c0b0a')
# Primary registers and SP preserved; PC/ADL/IFF are not preservation claims here.
mask=bytes.fromhex('ff '*20+'00 '*12)
assert len(mask)==32
payloads={
'run-start':(1,1,0,bytes.fromhex('01000100')+u32(1)+bytes.fromhex('11'*32+'22'*32+'33'*32+'44'*32),136),
'case-start':(2,2,1,bytes.fromhex('01000100')+bytes.fromhex('55'*32+'66'*32),68),
'observation':(3,3,1,bytes.fromhex('01000100000000000100600001000000')+entry+entry+mask,112),
'case-end':(4,4,1,bytes.fromhex('01000100')+u32(1)+u32(0)+u32(1)+bytes.fromhex('00000000'),20),
'checkpoint-error':(5,5,1,bytes.fromhex('01000200')+u32(1)+u32(4)+u32(3),16),
'run-end':(6,5,0,bytes.fromhex('01000000')+u32(1)+bytes(28)+bytes.fromhex('33'*32),68),
}
manifest={}
records={}
for name,(kind,seq,key,payload,expected_len) in payloads.items():
    assert len(payload)==expected_len
    header=bytes.fromhex('4d53545201')+bytes([kind])+bytes.fromhex('2800')+run+u32(seq)+u32(key)+u32(len(payload))+bytes(4)
    assert len(header)==40
    raw=header+payload
    assert crc_bitwise(raw)==zlib.crc32(raw)
    raw+=u32(crc_bitwise(raw))+b'\xa5'
    assert len(raw)==45+expected_len
    (ROOT/(name+'.bin')).write_bytes(raw)
    (ROOT/(name+'.hex')).write_text(raw.hex(' ')+'\n')
    records[name]=raw
    manifest[name]={'type':kind,'sequence':seq,'case_key':key,'payload_bytes':expected_len,'total_bytes':len(raw),'crc32':f'{crc_bitwise(raw[:-5]):08x}','sha256':hashlib.sha256(raw).hexdigest()}
# This nominal stream has illustrative hashes, so it is wire-valid only until
# real matching manifests are supplied. Never call it an authenticated run.
stream=b''.join(records[n] for n in ['run-start','case-start','observation','case-end','run-end'])
(ROOT/'nominal-wire-stream.bin').write_bytes(stream)
broken=bytearray(records['case-end']); broken[44]^=1
(ROOT/'bad-crc.bin').write_bytes(broken)
(ROOT/'missing-commit.bin').write_bytes(records['case-end'][:-1])
manifest['invalid']={'bad-crc.bin':'reject CRC; no verdict from this record','missing-commit.bin':'incomplete tail; no case completion'}
(ROOT/'expected-wire.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Exact control-slot bytes with explicit offsets/length.
slot=(b'MSTC'+u16(1)+u16(128)+run+u32(1)+u32(1)+u32(0)+u16(0)+bytes([1,0])+u32(0)+bytes.fromhex('22'*32+'33'*32)+bytes(12))
assert len(slot)==120
slot+=u32(crc_bitwise(slot))+b'\xa5'+bytes(3)
assert len(slot)==128
(ROOT/'control-slot.bin').write_bytes(slot)
(ROOT/'control-slot.hex').write_text(slot.hex(' ')+'\n')
# Snapshot controls use explicit deltas rather than production comparison code.
controls=[]
for seed in [0,1]:
    before=bytearray(entry)
    if seed:
        for i in range(17):before[i]^=0xff
    controls.append({'id':f'preserve-{seed}','entry':before.hex(),'exit':before.hex(),'changed_offsets':[],'expected':'no differences'})
    for label,offset in [('A',1),('BC-low',2),('BC-upper',4),('DE-low',5),('DE-upper',7),('HL-low',8),('HL-upper',10),('IX-low',11),('IX-upper',13),('IY-low',14),('IY-upper',16),('SP-low',17),('SP-upper',19)]:
        after=bytearray(before); after[offset]^=0x80
        controls.append({'id':f'{label}-{seed}','entry':before.hex(),'exit':after.hex(),'changed_offsets':[offset],'xor_mask':'80','expected':'one byte differs; all other bytes identical'})
    for bit in range(8):
        after=bytearray(before); after[0]^=1<<bit
        controls.append({'id':f'flag-{bit}-{seed}','entry':before.hex(),'exit':after.hex(),'changed_offsets':[0],'xor_mask':f'{1<<bit:02x}','expected':'only named flag bit differs'})
assert len(controls)==44
(ROOT/'capture-controls.json').write_text(json.dumps(controls,indent=2)+'\n')
# Report truth table has explicit, hand-chosen classifications.
plans=[
{'id':'all-pass','selected':[1,2],'ends':['PASSED','PASSED'],'assertions':[1,1],'failed_assertions':[0,0],'run_end':True,'verdict':'ALL TESTS PASSED','passed':2,'failed_tests':0},
{'id':'two-assertions-one-test','selected':[1,2],'ends':['FAILED','PASSED'],'assertions':[3,1],'failed_assertions':[2,0],'run_end':True,'verdict':'FAILURES','passed':1,'failed_tests':1},
{'id':'two-failing-tests','selected':[1,2],'ends':['FAILED','FAILED'],'assertions':[1,2],'failed_assertions':[1,2],'run_end':True,'verdict':'FAILURES','passed':0,'failed_tests':2},
{'id':'expected-error-pass','selected':[1],'ends':['PASSED'],'assertions':[1],'failed_assertions':[0],'run_end':True,'verdict':'ALL TESTS PASSED','passed':1,'failed_tests':0,'note':'API returned the expected nonzero error status'},
{'id':'missing-finalization','selected':[1],'ends':['PASSED'],'run_end':False,'verdict':'INCOMPLETE','passed':1,'failed_tests':0},
{'id':'missing-case','selected':[1,2],'ends':['PASSED',None],'run_end':True,'verdict':'INCOMPLETE','passed':1,'failed_tests':0},
{'id':'known-failure-then-fault','selected':[1,2],'ends':['FAILED',None],'run_end':False,'verdict':'INCOMPLETE','passed':0,'failed_tests':1},
{'id':'empty-plan','selected':[],'ends':[],'run_end':True,'verdict':'CONFIGURATION ERROR','passed':0,'failed_tests':0},
]
for status in ['OBSERVED','SKIPPED','UNSUPPORTED','BLOCKED','ERROR','INCOMPLETE']:
 plans.append({'id':status.lower(),'selected':[1,2],'ends':['PASSED',status],'run_end':True,'verdict':'INCOMPLETE' if status in ['ERROR','INCOMPLETE'] else 'NO FAILURES OBSERVED — coverage limited','passed':1,'failed_tests':0})
(ROOT/'report-oracles.json').write_text(json.dumps(plans,indent=2)+'\n')
print(f'Frozen oracles: {len(payloads)} record types, 44 capture vectors, {len(plans)} report scenarios.')
