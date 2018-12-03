def safe_send(sk, buf):
    total = 0
    buf = buf.encode()
    size = len(buf)

    sk.send(size.to_bytes(8, byteorder='little'))

    while total < size:
        total += sk.send(buf[total:])

    return

def safe_recv(sk):
    buf = bytearray()
    size = int.from_bytes(sk.recv(8), byteorder='little')
    total = 0

    while total < size:
        buf += sk.recv(size - total)
        total = len(buf)

    return buf.decode()
