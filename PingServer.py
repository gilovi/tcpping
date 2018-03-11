import socket
import struct
from contextlib import closing
from threading import Event, Thread

MAX_CONN = 5
TCP_PORT = 48888
UDP_PORT = 48889

stop = Event()


def serve_tcp():
    print 'TCP server initiated'
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind((socket.gethostbyname(socket.gethostname()), TCP_PORT))
        s.listen(MAX_CONN)
        while True:
            conn, _ = s.accept()
            conn.send(get_packet(conn))


def serve_udp():
    print 'UDP server initiated'
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
        s.bind((socket.gethostname(), UDP_PORT))
        while True:
            s.sendto(get_packet(s))


def get_packet(conn):
    data, addr = recvall(conn, 4)
    length, = struct.unpack('!I', data)
    data += recvall(conn, length)
    return data, addr


def recvall(sock, count):
    buf = b''
    addr = None
    while count:
        newbuf, addr = sock.recvfrom(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf, addr


if __name__ == '__main__':
    tcp_server = Thread(target=serve_tcp)
    udp_server = Thread(target=serve_udp)

    tcp_server.start()
    udp_server.start()

    print
    raw_input('press return to finish serving')
