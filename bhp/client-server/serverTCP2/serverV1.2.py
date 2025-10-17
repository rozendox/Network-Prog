import socket
import threading
import os
from datetime import datetime

# Configs do server
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12345  # Porta usada pelo servidor
DIRECTORY = 'files'  # Diretório para armazenar os arquivos
clients = {}  # Dicionário para armazenar os clientes conectados (nós)
messages = []  # Lista para armazenar as mensagens enviadas

# Cria o diretório de arquivos se não existir
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)


# Função para lidar com cada cliente
def handle_client(conn, addr):
    print(f'Cliente conectado: {addr}')
    conn.send("Conectado ao servidor!\n".encode())
    clients[addr] = conn  # Armazena o cliente conectado

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            command = data.split('|')[0].upper()

            if command == 'UPLOAD':
                try:
                    filename = data.split('|')[1]
                    file_content = data.split('|')[2]
                    with open(os.path.join(DIRECTORY, filename), 'w') as f:
                        f.write(file_content)
                    conn.send(f"Arquivo {filename} enviado com sucesso!\n".encode())
                except IndexError:
                    conn.send("Erro: Formato de comando UPLOAD incorreto.\n".encode())
                except Exception as e:
                    print(f"Erro no upload: {e}")
                    conn.send(f"Erro ao enviar o arquivo {filename}.\n".encode())

            elif command == 'DOWNLOAD':
                try:
                    filename = data.split('|')[1]
                    with open(os.path.join(DIRECTORY, filename), 'r') as f:
                        file_content = f.read()
                    conn.send(f"DOWNLOAD|{filename}|{file_content}\n".encode())
                except IndexError:
                    conn.send("Erro: Formato de comando DOWNLOAD incorreto.\n".encode())
                except FileNotFoundError:
                    conn.send(f"Erro: Arquivo {filename} não encontrado.\n".encode())
                except Exception as e:
                    print(f"Erro no download: {e}")
                    conn.send(f"Erro ao baixar o arquivo {filename}.\n".encode())

            elif command == 'LIST':
                try:
                    files = os.listdir(DIRECTORY)
                    file_list = ', '.join(files) if files else "Nenhum arquivo disponível"
                    conn.send(f"Arquivos disponíveis: {file_list}\n".encode())
                except Exception as e:
                    print(f"Erro ao listar arquivos: {e}")
                    conn.send("Erro ao listar arquivos.\n".encode())

            elif command == 'MESSAGE':
                try:
                    # Recebe o IP e a porta do destinatário como string
                    recipient_ip = data.split('|')[1]
                    message = data.split('|')[2]

                    # Converte o IP e a porta recebidos (em formato de string) para uma tupla
                    recipient_ip_port = eval(recipient_ip)  # Converte a string em tupla (ex: ('127.0.0.1', 63324))

                    # Registra a hora da mensagem
                    current_time = datetime.now().strftime('%H:%M:%S')

                    # Envia a mensagem para o nó destinatário
                    if recipient_ip_port in clients:
                        msg_with_time = f"MESSAGE from {addr[0]} at {current_time}: {message}"
                        clients[recipient_ip_port].send(f"{msg_with_time}\n".encode())
                        conn.send(f"Mensagem enviada para {recipient_ip_port}\n".encode())

                        # Armazena a mensagem
                        messages.append(f"From {addr[0]} to {recipient_ip_port[0]} at {current_time}: {message}")
                    else:
                        conn.send(f"Erro: Nó {recipient_ip_port} não encontrado.\n".encode())
                except IndexError:
                    conn.send("Erro: Formato de comando MESSAGE incorreto.\n".encode())

            elif command == 'LIST MESSAGES':
                try:
                    # Lista todas as mensagens armazenadas
                    if messages:
                        message_list = "\n".join(messages)
                    else:
                        message_list = "Nenhuma mensagem disponível."
                    conn.send(f"Mensagens:\n{message_list}\n".encode())
                except Exception as e:
                    conn.send(f"Erro ao listar mensagens: {e}\n".encode())

            else:
                conn.send("Comando inválido!\n".encode())

        except Exception as e:
            print(f"Erro na comunicação: {e}")
            conn.send("Erro na operação!\n".encode())
            break

    conn.close()
    del clients[addr]  # Remove o cliente da lista
    print(f'Cliente desconectado: {addr}')


# Inicia o servidor
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f'Servidor iniciado em {HOST}:{PORT}...')

    while True:
        conn, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()


if __name__ == "__main__":
    start_server()
