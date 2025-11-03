import sqlite3
import socket
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Função para criar o PDF com dados do banco
def gerar_pdf(dados):
    c = canvas.Canvas("dados_banco.pdf", pagesize=letter)
    width, height = letter
    y = height - 40  # Posição inicial no PDF

    c.drawString(30, y, "Dados do Banco de Dados:")
    y -= 20

    for tabela, linhas in dados.items():
        c.drawString(30, y, f"Tabela: {tabela}")
        y -= 20
        for linha in linhas:
            c.drawString(30, y, str(linha))
            y -= 20
        y -= 20  # Espaço entre tabelas

    c.save()


# Função para conectar ao banco de dados e executar operações
def executar_comando(comando):
    resposta = ""
    conn = sqlite3.connect("servidor.db")
    cursor = conn.cursor()

    try:
        if comando["acao"] == "criar_tabela":
            cursor.execute(comando["sql"])
            conn.commit()
            resposta = "Tabela criada com sucesso."

        elif comando["acao"] == "remover_tabela":
            cursor.execute(f"DROP TABLE IF EXISTS {comando['nome_tabela']}")
            conn.commit()
            resposta = "Tabela removida com sucesso."

        elif comando["acao"] == "alterar_tabela":
            cursor.execute(comando["sql"])
            conn.commit()
            resposta = "Tabela alterada com sucesso."

        elif comando["acao"] == "ver_tabelas":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = cursor.fetchall()
            resposta = [tabela[0] for tabela in tabelas]

        elif comando["acao"] == "gerar_pdf":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = cursor.fetchall()
            dados = {}
            for tabela in tabelas:
                cursor.execute(f"SELECT * FROM {tabela[0]}")
                dados[tabela[0]] = cursor.fetchall()
            gerar_pdf(dados)
            resposta = "PDF gerado com sucesso."

    except sqlite3.Error as e:
        resposta = f"Erro no banco de dados: {str(e)}"
    finally:
        conn.close()

    return resposta


# Configuração do servidor UDP
servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor_socket.bind(("localhost", 12345))

print("Servidor UDP rodando e aguardando comandos...")

while True:
    data, addr = servidor_socket.recvfrom(1024)
    comando = json.loads(data.decode())
    resposta = executar_comando(comando)
    servidor_socket.sendto(json.dumps(resposta).encode(), addr)

