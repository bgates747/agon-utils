"""Independent qualification parser, not the W05 production report decoder."""
import struct,zlib

def records(data):
    result=[];offset=0
    while offset<len(data):
        if len(data)-offset<40:raise ValueError('truncated header')
        h=data[offset:offset+40]
        if h[:5]!=b'MSTR\x01' or h[5] not in range(1,7) or h[6:8]!=b'\x28\0' or h[36:40]!=bytes(4):raise ValueError('header')
        n=struct.unpack_from('<I',h,32)[0]
        if not 2<=n<=1024:raise ValueError('length')
        end=offset+45+n
        if end>len(data):raise ValueError('truncated record')
        rec=data[offset:end]
        if rec[-1]!=0xa5:raise ValueError('commit')
        if struct.unpack_from('<I',rec,len(rec)-5)[0]!=zlib.crc32(rec[:-5]):raise ValueError('CRC')
        if rec[40:42]!=b'\x01\0':raise ValueError('payload version')
        result.append((h[5],int.from_bytes(h[24:28],'little'),int.from_bytes(h[28:32],'little'),rec[40:-5],h[8:24]))
        offset=end
    return result

def slots(data):
    found=[]
    for offset in [0,128]:
        b=data[offset:offset+128]
        if b[:8]!=b'MSTC\x01\0\x80\0' or b[124]!=0xa5:continue
        if b[39] or b[108:120]!=bytes(12) or b[125:]!=bytes(3):continue
        if zlib.crc32(b[:120])!=int.from_bytes(b[120:124],'little'):continue
        generation,next_seq,confirmed,used,state=struct.unpack_from('<IIIHB',b,24)
        if not generation or not next_seq or confirmed>=next_seq or used>2048 or state not in range(1,7):continue
        found.append({'generation':generation,'next':next_seq,'confirmed':confirmed,'used':used,'state':state,'run':b[8:24].hex()})
    return found
