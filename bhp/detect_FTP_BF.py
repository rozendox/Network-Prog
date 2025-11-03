from scapy.all import *
from collections import defaultdict
from datetime import datetime, timedelta

# Configuração do script
FTP_PORT = 21
THRESHOLD_ATTEMPTS = 10  # Número de tentativas permitido antes de marcar como suspeito
TIME_WINDOW = timedelta(seconds=60)  # Janela de tempo para detectar força bruta

# Dicionário para armazenar tentativas de login por IP
login_attempts = defaultdict(list)


def detect_ftp_brute_force(packet):
    if packet.haslayer(TCP) and packet[TCP].dport == FTP_PORT:
        # Captura o conteúdo da carga útil
        payload = bytes(packet[TCP].payload).decode('utf-8', errors='ignore')

        # Detecta tentativas de login
        if "USER" in payload or "PASS" in payload:
            src_ip = packet[IP].src
            timestamp = datetime.now()
            login_attempts[src_ip].append(timestamp)

            # Limpa tentativas antigas fora da janela de tempo
            login_attempts[src_ip] = [
                attempt for attempt in login_attempts[src_ip]
                if attempt > timestamp - TIME_WINDOW
            ]

            # Verifica se excedeu o limite de tentativas
            if len(login_attempts[src_ip]) > THRESHOLD_ATTEMPTS:
                print(
                    f"[ALERTA] Possível ataque de força bruta detectado! IP: {src_ip}, Tentativas: {len(login_attempts[src_ip])}")


def main():
    print("Monitorando tráfego FTP para detectar ataques de força bruta...")
    sniff(filter=f"tcp port {FTP_PORT}", prn=detect_ftp_brute_force)


if __name__ == "__main__":
    main()
