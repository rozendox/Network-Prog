import socket

# Configurações do cliente
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12346  # Porta usada pelo servidor


def client_program():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # O NODE RECEBE A MENSAGEM DE CONEXÃO
    print(client.recv(1024).decode())

    while True:
        command = input("Digite o comando (UPLOAD, DOWNLOAD, LIST, MESSAGE, LIST MESSAGES): ")

        # criar arquivo
        if command.upper() == 'UPLOAD':
            filename = input("Nome do arquivo: ")
            file_content = input("Conteúdo do arquivo: ")
            message = f'UPLOAD|{filename}|{file_content}'
        # Baixar arquivo
        elif command.upper() == 'DOWNLOAD':
            filename = input("Nome do arquivo: ")
            message = f'DOWNLOAD|{filename}'
        # listar arquivos
        elif command.upper() == 'LIST':
            message = 'LIST'
        # enviar mensagem para outro nó
        elif command.upper() == 'MESSAGE':
            recipient_ip = input("Digite o IP e porta do nó destinatário (exemplo: ('127.0.0.1', 63324)): ")
            msg_content = input("Digite a mensagem: ")
            message = f'MESSAGE|{recipient_ip}|{msg_content}'
        # listar mensagens recebidas/enviadas
        elif command.upper() == 'LIST MESSAGES':
            message = 'LIST MESSAGES'
        else:
            print("Comando inválido!")
            continue

        client.send(message.encode())
        response = client.recv(1024).decode()
        print(f"Resposta do servidor: {response}")


if __name__ == "__main__":
    client_program()
