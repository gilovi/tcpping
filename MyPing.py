from __future__ import division

import socket
import struct
import time
from contextlib import closing

TCP_PORT = 48888
UDP_PORT = 48889


class MyPing:
    def __init__(self, ip, udp, timeout, count, packetsize):
        """

        :param ip:
        :param udp:
        :param timeout:
        :param count:
        :param packetsize: Packet size. minimum 8 bytes. Smaller values are completed to 8.
        :param interval:
        """
        # self.interval = interval
        self.interval = 1
        self.packetsize = 8 if (not packetsize or packetsize < 8) else packetsize
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
        addr = (self.ip, UDP_PORT)
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.settimeout(self.timeout)
            for i in range(self.count):
                s.sendto(self.packet, addr)
                out_timestamp = time.time() * 1000
                try:
                    while self.get_seq(s.recv(self.packetsize)) <= i:
                        pass
                except socket.timeout:
                    continue
                in_timestamp = time.time() * 1000
                rt = in_timestamp - out_timestamp
                self.roundtrips.append(rt)
                print 'Reply from {ip}: bytes={size} rt={rt}'.format(ip=self.ip, size=self.packetsize, rt=rt)
                time.sleep(self.interval)

            if self.roundtrips:
                print 'average roundtrip time in ms:', self.average()
            print 'Packets: Sent = {count}, Received = {received}, Lost = {lost}'.format(count=self.count,
                                                                                         received=len(
                                                                                             self.roundtrips),
                                                                                         lost=self.count - len(
                                                                                             self.roundtrips))

    def send_tcp(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.connect((self.ip, TCP_PORT))
            except Exception as e:
                print 'Could not create connection with server.', e
                return
            s.settimeout(self.timeout)
            for i in range(self.count):
                s.sendall(self.packet)
                out_timestamp = time.time() * 1000
                try:
                    while self.get_seq(s.recv(self.packetsize)) <= i:
                        pass
                except socket.timeout:
                    continue

                in_timestamp = time.time() * 1000
                rt = in_timestamp - out_timestamp
                self.roundtrips.append(rt)
                print 'Reply from {ip}: bytes={size} time={rt}'.format(ip=self.ip, size=self.packetsize, rt=rt)
                time.sleep(self.interval)

            if self.roundtrips:
                print 'average roundtrip time in ms:', self.average()
            print 'Packets: Sent = {count}, Received = {received}, Lost = {lost}'.format(count=self.count,
                                                                                         received=len(self.roundtrips),
                                                                                         lost=self.count - len(
                                                                                             self.roundtrips))

    def average(self):
        if not self.roundtrips:
            raise AttributeError('No roundtrip data')

        return sum(self.roundtrips) / len(self.roundtrips)

    def get_seq(self, packet):
        return struct.unpack('!I', packet[4:8])[0]
