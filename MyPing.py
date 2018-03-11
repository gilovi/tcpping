import select
import socket
import struct
import time
from contextlib import closing

TCP_PORT = 48888
UDP_PORT = 48889


class MyPing:
    def __init__(self, ip, udp, timeout, count, packetsize, interval):
        """

        :param ip:
        :param udp:
        :param timeout:
        :param count:
        :param packetsize: Packet size. minimum 8 bytes. Smaller values are completed to 8.
        :param ttl:
        :param interval:
        """
        # self.interval = interval
        self.packetsize = 8 if (not packetsize or packetsize < 8) else self.packetsize
        self.count = 4 if not count else count
        self.timeout = timeout
        self.udp = udp
        self.ip = ip
        self.seq = 0
        self.roundtrips = []

    @property
    def packet(self):
        """
        The packet to send over the wire.
        message is constructed from one byte of length, one byte of seq number and the rest is garbage data.
        :return:
        """
        while True:
            self.seq += 1
            return struct.pack('!I', self.packetsize - 4) + struct.pack('!I', self.seq) + ('0' * (self.packetsize - 8))

    def send(self):
        if self.udp:
            self.send_udp()
        else:
            self.send_tcp()

    def send_udp(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.sendto(self.packet, (self.ip, UDP_PORT))

    def send_tcp(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.connect((self.ip, TCP_PORT))
            except Exception as e:
                print e
                return

            s.settimeout(self.timeout)
            s.sendall(self.packet)
            out_timestamp = time.time()
            select.select([s], [], [])
            print s.recv(self.packetsize)
            in_timestamp = time.time()
            rt = in_timestamp - out_timestamp
            print rt
