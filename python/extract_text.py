arg_null = 0
arg_x32 = 4
arg_i32 = 4
arg_i16 = 2
arg_i8i8 = 2
arg_i8 = 1

opcode_len = {
    b'\x00': arg_null,
    b'\x01': arg_i8i8,
    b'\x02': arg_x32,
    b'\x03': arg_i16,
    b'\x04': arg_null,
    b'\x05': arg_null,
    b'\x06': arg_x32, #jmp
    b'\x07': arg_x32,
    b'\x08': arg_null,
    b'\x09': arg_null,
    b'\x0a': arg_i32,
    b'\x0b': arg_i16,
    b'\x0c': arg_i8,
    b'\x0d': arg_x32,
    #b'\x0e': OPARG_STRING, #push string
    b'\x0f': arg_i16,
    b'\x10': arg_i8,
    b'\x11': arg_i16,
    b'\x12': arg_i8,
    b'\x13': arg_null,
    b'\x14': arg_null,
    b'\x15': arg_i16,
    b'\x16': arg_i8,
    b'\x17': arg_i16,
    b'\x18': arg_i8,
    b'\x19': arg_null,
    b'\x1a': arg_null,
    b'\x1b': arg_null,
    b'\x1c': arg_null,
    b'\x1d': arg_null,
    b'\x1e': arg_null,
    b'\x1f': arg_null,
    b'\x20': arg_null,
    b'\x21': arg_null,
    b'\x22': arg_null,
    b'\x23': arg_null,
    b'\x24': arg_null,
    b'\x25': arg_null,
    b'\x26': arg_null,
    b'\x27': arg_null,
}

import sys

def extract_text(filename, entry = 0):
    out = open("output.txt", "w", encoding = 'utf8', errors = 'replace')
    f = open(filename, "rb")
    oplen = int.from_bytes(f.read(4), byteorder='little')
    pos = f.tell()
    while pos < oplen:
        opcode = f.read(1)
        if opcode == b'\x0e' :
            offset = int.from_bytes(f.read(1), byteorder='little')
            data = f.read(offset - 1);
            if pos >= entry :
                out.write(str(data, encoding = 'shiftjis', errors = 'replace') + '\n')
            f.read(1)
        else :
            if opcode in opcode_len:
                if opcode_len[opcode] != arg_null:
                    f.read(opcode_len[opcode])
            else:
                print("opcode 0x%x is invalid" % int.from_bytes(opcode, byteorder='little'))
                out.close()
                f.close()
                exit()
        pos = f.tell()
    f.read(10)
    offset = int.from_bytes(f.read(1), byteorder='little')
    out.write(str(f.read(offset - 1), encoding = 'shiftjis', errors = 'replace') + '\n')
    out.close()
    f.close()

if __name__ == "__main__" :
    argc = len(sys.argv)
    if argc < 2 :
        print("please input hcb file")
    filename = sys.argv[1]
    extract_text(filename)
