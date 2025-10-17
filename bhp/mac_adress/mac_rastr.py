import socket
import requests

def get_mac_address():
    # Obter o endereço MAC da interface de rede
    mac_address = socket.gethostbyname(socket.gethostname())
    return mac_address

def send_data_to_server(mac_address):
    # URL do servidor para enviar os dados
    url = "http://your-server.com/api/mac"

    # Dados a serem enviados
    data = {"mac_address": mac_address}

    # Enviar os dados para o servidor
    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("Dados enviados com sucesso!")
    else:
        print("Falha ao enviar dados:", response.status_code)

if __name__ == "__main__":
    mac_address = get_mac_address()
    send_data_to_server(mac_address)