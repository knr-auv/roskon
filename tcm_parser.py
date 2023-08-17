import numpy as np

class DummyPort:
    def __init__(self) -> None:
        self.dummy_data = bytearray([0,3,4,2,34,54,56])
        self.pointer = 0

    def read(self, size=1):
        ret = self.dummy_data[self.pointer]
        self.pointer = (self.pointer + 1) % len(self.dummy_data) 
        return ret

def receive_msg(port):  # TODO REFACTOR less code
    try:
        b = port.read(size=1)[0] & 0xFF
        if b != 0x69:
            return
        b = port.read(size=1)[0] & 0xFF
        if b != 0x68:
            return
        MSB = LSB = 0
        MSB = port.read(size=1)[0] & 0xFF
        LSB = port.read(size=1)[0] & 0xFF
        dataLen = (MSB << 8 | LSB) & 0xFFFF
        msg_type = port.read(size=1)[0] & 0xFF
        rx_buffer = bytearray(180)
        rx_buffer[0] = 0x69
        rx_buffer[1] = 0x68
        rx_buffer[2] = MSB
        rx_buffer[3] = LSB
        rx_buffer[4] = msg_type
        data = bytearray(dataLen)
        for i in range(dataLen):
            data[i] = port.read(size=1)[0] & 0xFF
            rx_buffer[i + 5] = data[i]
        rx_buffer[5 + dataLen] = port.read(size=1)[0] & 0xFF
        rx_buffer[5 + dataLen + 1] = port.read(size=1)[0] & 0xFF
        if (compare_checksum(0, rx_buffer, len(rx_buffer)) == False):
            return
        return data, msg_type
        # ParseData(data, msg_type)

    except Exception as err:
        print("epic fail", err)

def receive_msg_refactored(port) -> (bytearray, int):  # TODO REFACTORed UNBUG!
    try:
        rx_buffer = port.read(size=5)
        if rx_buffer[0] != 0x69 or rx_buffer[1] != 0x68:
            return
        MSB = rx_buffer[2]
        LSB = rx_buffer[3]
        dataLen = (MSB << 8 | LSB) & 0xFFFF
        msg_type = rx_buffer[4]
        rx_buffer.extend(bytearray(dataLen+2))
        data = bytearray(dataLen)
        for i in range(dataLen):
            data[i] = port.read(size=1)[0] & 0xFF
            rx_buffer[i + 5] = data[i]
        rx_buffer[5 + dataLen] = port.read(size=1)[0] & 0xFF
        rx_buffer[5 + dataLen + 1] = port.read(size=1)[0] & 0xFF
        if (compare_checksum(0, rx_buffer, len(rx_buffer)) == False):
            return
        return data, msg_type

    except Exception as err:
        print("epic fail", err)        

def create_msg(msg_type: int, data: bytes) -> bytearray:
    l = len(data) if data is not None else 0
    l = np.uint16(l)
    msg = bytearray(l + 7)

    msg[0] = 0x69
    msg[1] = 0x68
    msg[2] = l >> 8
    msg[3] = l & 0xFF
    msg[4] = msg_type

    for i in range(l):
        msg[i+5] = data[i]

    checksum = calculate_checksum(msg, 0, l+5)
    msg[l + 5] = (checksum >> 8) & 0xFF
    msg[l + 6] = (checksum & 0xFF)
    return msg


def calculate_checksum(data: bytes, offset: int,  length: int) -> int:
    x = 0
    crc = 0xFFFF

    for i in range(length):
        x = (((crc >> 8) ^ data[i])) & 0xFF
        x ^= (x >> 4) & 0xFF
        crc = ((crc << 8) ^ ((x << 12)) ^ ((x << 5)) ^ (x)) & 0xFFFF
    return crc


def compare_checksum(header_index: int, rx_buffer, buffer_size) -> bool:
    receivedChecksum = MSB = LSB = 0
    MSB = rx_buffer[(header_index + 2) % buffer_size]
    LSB = rx_buffer[(header_index + 3) % buffer_size]
    dataLen = (MSB << 8 | LSB)

    len = dataLen + 7
    calculated_checksum = calculate_checksum(rx_buffer, header_index, len - 2)

    MSB = rx_buffer[(header_index + len - 2) % buffer_size]
    LSB = rx_buffer[((header_index + len - 1) % buffer_size)]
    receivedChecksum = (MSB << 8 | LSB)

    return receivedChecksum == calculated_checksum


def floats_to_bytes(values) -> bytearray:
    data = np.array(values, dtype="float32").tobytes()
    return data

# 0x69  header
# 0x68  header
# 0x0   len
# 0x4   len
# 0x3   msg type
# 0x0   data
# 0x0   data
# 0x0   data
# 0x40  data
# 0x11  crc
# 0x5e  crc


if __name__ == "__main__":
    floats = [float(2)]
    data = floats_to_bytes(floats)
    x = create_msg(0x3, data)

    print(floats)
    print(data)
    print(x)

    for b in x:
        print(hex(b))

    dummy_port = DummyPort()
    dummy_port.dummy_data = x
    
    receive_msg(dummy_port, None)
