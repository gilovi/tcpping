import socket
import struct
from contextlib import closing
from threading import Event, Thread

MAX_CONN = 1
TCP_PORT = 48888
UDP_PORT = 48889
DEFAULT_TIMEOUT = 5
stop = Event()


def serve_tcp_client(conn):
    conn.settimeout(DEFAULT_TIMEOUT)
    while True:
        try:
            data = get_packet(conn)
        except socket.error:
            break
        conn.send(data)


def serve_tcp():
    print 'TCP server initiated'
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((socket.gethostbyname(socket.gethostname()), TCP_PORT))
        s.listen(MAX_CONN)
        while True:
            conn, _ = s.accept()
            Thread(target=serve_tcp_client, args=(conn,)).start()


def serve_udp():
    print 'UDP server initiated'
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((socket.gethostname(), UDP_PORT))
        while True:
            try:
                p, addr = s.recvfrom(1024)
                s.sendto(p, addr)
            except socket.error:
                break
    Thread(target=serve_udp).start()


def get_packet(conn):
    data = recvall(conn, 4)
    length, = struct.unpack('!I', data)
    payload = recvall(conn, length)
    return data + payload


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            raise socket.error
        buf += newbuf
        count -= len(newbuf)
    return buf


if __name__ == '__main__':
    tcp_server = Thread(target=serve_tcp)
    udp_server = Thread(target=serve_udp)

    tcp_server.start()
    udp_server.start()

    print
    raw_input('press return to finish serving')
