import socket
import json

# Função para enviar comandos para o servidor
def enviar_comando(comando):
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente_socket.sendto(json.dumps(comando).encode(), ("localhost", 12345))
    resposta, _ = cliente_socket.recvfrom(1024)
    print("Resposta do servidor:", json.loads(resposta.decode()))
    cliente_socket.close()

# Exemplo de uso das funções do cliente
# Criar uma tabela
comando = {
    "acao": "criar_tabela",
    "sql": "CREATE TABLE IF NOT EXISTS exemplo (id INTEGER PRIMARY KEY, nome TEXT, idade INTEGER)"
}
enviar_comando(comando)

# Remover uma tabela
comando = {
    "acao": "remover_tabela",
    "nome_tabela": "exemplo"
}
enviar_comando(comando)

# Alterar uma tabela (adicionar uma coluna)
comando = {
    "acao": "alterar_tabela",
    "sql": "ALTER TABLE exemplo ADD COLUMN endereco TEXT"
}
enviar_comando(comando)

# Ver tabelas
comando = {
    "acao": "ver_tabelas"
}
enviar_comando(comando)

# Gerar PDF com dados do banco de dados
comando = {
    "acao": "gerar_pdf"
}
enviar_comando(comando)
