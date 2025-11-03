import mysql.connector

# Informações do banco de dados
DATABASE = "nome_do_banco"
USER = "usuario"
PASSWORD = "senha"
HOST = "endpoint_do_banco"  # URL do banco de dados em nuvem

try:
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    print("Conexão bem-sucedida ao banco de dados.")

    # Criar cursor e tabela de exemplo
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exemplo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(50),
            idade INT
        );
    """)
    conn.commit()
    print("Tabela criada com sucesso.")

    # Fechar cursor e conexão
    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print(f"Erro: {err}")
