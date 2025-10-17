import paramiko
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

# Configurações do SSH
ssh_host = '127.0.0.1'
ssh_port = 22
ssh_username = 'roxypy'
ssh_password = 'lovepython'

# Configurações do Proxy SOCKS
proxy_host = '127.0.0.1'
proxy_port = 1080


# Função para configurar o túnel SSH
def create_ssh_tunnel():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)
        print("Túnel SSH criado com sucesso.")
        return ssh
    except paramiko.ssh_exception.SSHException as e:
        print(f"Erro ao criar o túnel SSH: {e}")
        return None


# Função para configurar o proxy SOCKS
def create_socks_proxy():
    class SocksHTTPAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            kwargs['proxy'] = f'socks://{proxy_host}:{proxy_port}'
            return super(SocksHTTPAdapter, self).init_poolmanager(*args, **kwargs)

    session = requests.Session()
    session.mount('http://', SocksHTTPAdapter())
    session.mount('https://', SocksHTTPAdapter())
    return session


# Criar o túnel SSH
ssh = create_ssh_tunnel()
if ssh:
    # Criar o proxy SOCKS
    session = create_socks_proxy()

    # Testar a conexão através do proxy SOCKS
    try:
        response = session.get('http://www.google.com')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o site: {e}")

    # Fe```python
    # Fechar a conexão SSH
    ssh.close()
else:
    print("Falha ao criar o túnel SSH. Verifique as credenciais e a conectividade de rede.")