class InitialSave(object):
    def __init__(self, log = True):
        self.table = {}
        self.log = log


    # will set the bits of value to the offset in the save (or'ing them with what is already there)
    def set_bits(self, offset, value, filter=None):

        if filter and not filter(value):
            return

        if offset in self.table:
            self.table[offset][1] |= value
        else:
            self.table[offset] = [0x00, value]


    # will overwrite the byte at offset with the given value
    def set_byte(self, offset, value, filter=None):

        if filter and not filter(value):
            return

        if offset in self.table:
            v = self.table[offset]
            if v[0] == 1:
                print("duplicate byte write error at offset {:04x}".format(offset))
            else:
                self.table[offset][0] = 1
                self.table[offset][1] = value | v[1]
        else:
            self.table[offset] = [0x01, value]


    # will overwrite the byte at offset with the given value
    def set_bytes(self, offset, bytes, filter=None):
        for i, value in enumerate(bytes):
            self.set_byte(offset + i, value, filter)


    def set_switch_flag(self, scene, flag, filter=None):
        offset = 0xF8 + (scene * 0x1C) + 4 + flag_to_offset(flag)
        bit = flag & 0x7
        value = 1 << bit
        self.set_bits(offset, value, filter)


    # will overwrite the byte at offset with the given value
    def write_table_to_rom(self, rom):
        t = []
        for offset, v in self.table.items():
            type = v[0]
            value = v[1]
            t += [(offset & 0xFF00) >> 8, offset & 0xFF, type, value]
            if self.log:
                print("{} {:08x} {:04x} {:02x}".format(type, 0x801EF670 + offset, offset, value))


        t += [0, 0, 0, 0] # terminator
        table_len = len(t)

        start = rom.sym("INITIAL_SAVE_DATA")
        end = rom.sym("INITIAL_SAVE_DATA_END")
        size = end - start
        if self.log:
            print("Initial save table capacity: 0x{:03X}/0x{:03X}".format(table_len, size))
        if table_len > size:
            raise Exception("The initial save table has exceeded it's maximum capacity: 0x{:03X}/0x{:03X}".format(table_len, size))
        rom.write_bytes(start, t)


def flag_to_offset(flag):
    offset = (flag // 0x20) * 4
    w = (flag & 0x18) >> 3
    return offset + 3 - w
