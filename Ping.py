import argparse

from MyPing import MyPing


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip')
    parser.add_argument('--udp', action='store_true',
                        help="configures the protocol to be UDP instead of the default TCP")
    parser.add_argument('--timeout', '-W', type=int, help="Time to wait for a response, in seconds.")
    parser.add_argument('--count', '-c', type=int, help="Stop after sending count 'ping' packets")
    parser.add_argument('--packetsize', '-s', type=int, help="Specifies the number of data bytes to be sent")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    ping = MyPing(ip=args.ip, udp=args.udp, timeout=args.timeout, count=args.count, packetsize=args.packetsize)
    ping.send()
