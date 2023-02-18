arg_null = 0
arg_x32 = 4
arg_i32 = 4
arg_i16 = 2
arg_i8i8 = 2
arg_i8 = 1

opcode_len = {
    0x00: arg_null,
    0x01: arg_i8i8,
    0x02: arg_x32,
    0x03: arg_i16,
    0x04: arg_null,
    0x05: arg_null,
    0x06: arg_x32, #jmp
    0x07: arg_x32,
    0x08: arg_null,
    0x09: arg_null,
    0x0a: arg_i32,
    0x0b: arg_i16,
    0x0c: arg_i8,
    0x0d: arg_x32,
    #0x0e: OPARG_STRING, #push string
    0x0f: arg_i16,
    0x10: arg_i8,
    0x11: arg_i16,
    0x12: arg_i8,
    0x13: arg_null,
    0x14: arg_null,
    0x15: arg_i16,
    0x16: arg_i8,
    0x17: arg_i16,
    0x18: arg_i8,
    0x19: arg_null,
    0x1a: arg_null,
    0x1b: arg_null,
    0x1c: arg_null,
    0x1d: arg_null,
    0x1e: arg_null,
    0x1f: arg_null,
    0x20: arg_null,
    0x21: arg_null,
    0x22: arg_null,
    0x23: arg_null,
    0x24: arg_null,
    0x25: arg_null,
    0x26: arg_null,
    0x27: arg_null,
}

import sys

def repack(hcb, text, output = "output.hcb"):
    str_addr = []
    jmp_addr = []
    addr_offset = {}
    oplen = int.from_bytes(hcb[0: 4], byteorder='little')
    entry = int.from_bytes(hcb[oplen: oplen + 4], byteorder='little')

    title_pos = oplen + 10
    pos = title_pos + 1 + hcb[title_pos]
    sys_func_num = int.from_bytes(hcb[pos: pos + 2], byteorder='little')
    pos += 2
    thread_start_index = -1
    for i in range(0, sys_func_num) :
        pos += 1
        func_len = hcb[pos]
        pos += 1
        func_name = str(hcb[pos: pos + func_len - 1], encoding = "utf8")
        if func_name == "ThreadStart":
            thread_start_index = i
            break
        pos += func_len
    if thread_start_index == -1:
        print("system function ThreadStart not found!")
        exit()

    pos = 4
    while pos < oplen:
        opcode = hcb[pos]
        pos += 1
        if opcode == 0x0e :
            str_addr.append(pos)
            pos += 1 + hcb[pos]
        elif opcode == 0x02 or opcode == 0x06 or opcode == 0x07:
            addr = int.from_bytes(hcb[pos: pos + 4], byteorder='little')
            jmp_addr.append((pos, addr))
            addr_offset[addr] = 0
            pos += 4
        elif opcode == 0x0a:
            if hcb[pos + 4] == 0x3 and int.from_bytes(hcb[pos + 5: pos + 7], byteorder='little') == thread_start_index:
                addr = int.from_bytes(hcb[pos: pos + 4], byteorder='little')
                jmp_addr.append((pos, addr))
                addr_offset[addr] = 0
                pos += 7
            else:
                pos += 4
        else :
            if opcode in opcode_len:
                pos += opcode_len[opcode]
            else:
                print("pos 0x%x opcode 0x%x is invalid" % (pos, opcode))
                exit()
    str_addr.append(title_pos)

    str_index = 0
    jmp_index = 0
    cur_off = 0
    str_num = len(text) - 1 #the last line is for title
    addr_offset[entry] = 0
    arr = sorted(addr_offset)
    for addr in arr:
        while str_index < str_num and addr > str_addr[str_index]:
            strlen = len(text[str_index])
            if strlen > 0:
                cur_off += strlen + 1 - hcb[str_addr[str_index]]
            str_index += 1
        addr_offset[addr] = cur_off
    hcb[0:4] = (oplen + cur_off).to_bytes(4, byteorder='little')
    hcb[oplen: oplen + 4] = (entry + addr_offset[entry]).to_bytes(4, byteorder='little')
    for _pos, _addr in jmp_addr:
        hcb[_pos: _pos + 4] = (_addr + addr_offset[_addr]).to_bytes(4, byteorder='little')

    with open(output, "wb") as f:
        pos = 0
        for str_index in range(0, str_num + 1):
            addr = str_addr[str_index]
            f.write(hcb[pos: addr])
            strlen = len(text[str_index])
            pos = addr + hcb[addr]
            if strlen > 0:
                f.write((strlen + 1).to_bytes(1, byteorder='little'))
                f.write(text[str_index])
            else:
                f.write(hcb[addr: pos])
        f.write(hcb[pos:])

if __name__ == "__main__" :
    argc = len(sys.argv)
    if argc < 3:
        print("please input hcb and text file")
    hcbfile = sys.argv[1]
    txtfile = sys.argv[2]
    with open(hcbfile, "rb") as f:
        hcb = bytearray(f.read())
 
    text = []
    cnt = 0
    with open(txtfile, "r", encoding = 'utf-8', errors = 'surrogateescape') as f:
        lines = f.readlines()
        for line in lines:
            strlen = len(line)
            if strlen > 1 and line[0] == '@':
                text.append(line[1: strlen - 1].encode("gbk", errors = 'surrogateescape'))
            else:
                text.append([])
    repack(hcb, text)