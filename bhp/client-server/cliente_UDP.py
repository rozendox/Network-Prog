import socket

target_host = '127.0.0.1'
target_port = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b"aaabbbccc", (target_host, target_port))

try:
    data, address = client.recvfrom(4096)
    print(f'Received {data} from {address}')
except ConnectionResetError as e:
    print(f"ConnectionResetError: {e}")
finally:
    client.close()