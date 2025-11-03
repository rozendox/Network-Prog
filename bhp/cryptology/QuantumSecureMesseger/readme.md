````
______      ______  ___   __    ______      
/_____/\    /_____/\/__/\ /__/\ /_____/\     
\:::_ \ \   \:::__\/\::\_\\  \ \\:::_ \ \    
 \:(_) ) )_    /: /  \:. `-\  \ \\:\ \ \ \   
  \: __ `\ \  /::/___ \:. _    \ \\:\ \ \ \  
   \ \ `\ \ \/_:/____/\\. \`-\  \ \\:\/.:| | 
    \_\/ \_\/\_______\/ \__\/ \__\/ \____/_/ 
                                             
                                             
````                                          

# QuantumSecureMessenger

**QuantumSecureMessenger** é um sistema de comunicação **altamente seguro** e **pós-quântico** que utiliza algoritmos de última geração para proteger trocas de mensagens em ambientes distribuídos. Este repositório é ideal para estudos avançados em segurança, criptografia moderna e engenharia de software, além de ser uma base sólida para aplicações críticas.

---

## **Recursos**

### 🔒 **Segurança de Classe Mundial**
- **Criptografia Pós-Quântica** com o algoritmo **Kyber512** para troca de chaves e **Dilithium** para assinaturas digitais.
- **Perfect Forward Secrecy (PFS)**: Mesmo que uma chave seja comprometida, comunicações anteriores permanecem seguras.
- **TLS** para proteger o transporte das mensagens na rede.

### 📡 **Comunicação Assíncrona Multiusuário**
- Suporte para vários clientes conectados ao servidor simultaneamente.
- Mecanismo de autenticação mútua entre cliente e servidor.

### 🗂️ **Persistência de Dados**
- Banco de dados SQLite para armazenar usuários, chaves e mensagens.
- Logs detalhados para rastrear atividades.

### 🌐 **Interface Web**
- Painel de gerenciamento com **Flask** e **WebSocket** para monitoramento em tempo real.
- Visualização de mensagens trocadas e gerenciamento de chaves.

### ⚙️ **Modularidade e Escalabilidade**
- Arquitetura modular para fácil extensão e integração.
- Suporte para ambientes distribuídos e balanceamento de carga.

---

## **Tecnologias Utilizadas**
- **Python 3.8+**
- **pqcrypto**: Biblioteca de algoritmos pós-quânticos.
- **asyncio**: Comunicação assíncrona eficiente.
- **cryptography**: TLS e funções de hashing seguras.
- **SQLAlchemy**: Integração com banco de dados SQLite.
- **Flask**: Interface web para monitoramento.
- **WebSocket**: Atualizações em tempo real.

---

## **Instalação e Configuração**

### Pré-requisitos
- **Python 3.8+**
- Pip para gerenciar pacotes Python.

### 1. Clone o repositório
bash

``git clone https://github.com/seu-usuario/QuantumSecureMessenger.git``

``cd QuantumSecureMessenger``
2. Instale as dependências
bash<br>
``pip install -r requirements.txt``<br>
<br>
3. Geração de Certificados TLS<br>
Para comunicação segura, gere um certificado TLS:<br>
``openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem``<br>
<br>
5. Configuração do Banco de Dados<br>
O banco de dados será criado automaticamente no primeiro uso. Para criar as tabelas manualmente:<br>

python<br>
``-c "from database import Base, engine; Base.metadata.create_all(bind=engine)"``<br>

Como Usar<br>

1. Iniciar o Servidor<br>
Execute o servidor para escutar conexões de clientes:<br>

no terminal:<br>
``python server.py``<br>
2. Enviar Mensagens<br>
Utilize o cliente para enviar mensagens criptografadas:<br>

``python client.py``<br>
3. Monitoramento via Painel Web<br>
Inicie o painel para monitorar mensagens e gerenciar usuários:<br>

bash<br>
Copiar código<br>
python web_app.py<br>
Acesse http://127.0.0.1:5000 no navegador.<br>

Arquitetura do Projeto
Estrutura de Pastas

```QuantumSecureMessenger/
├── database.py          # Gerenciamento do banco de dados<br>
├── server.py            # Servidor assíncrono<br>
├── client.py            # Cliente para envio de mensagens<br>
├── web_app.py           # Painel de monitoramento Flask<br>
├── cert.pem             # Certificado TLS<br>
├── key.pem              # Chave privada TLS<br>
├── requirements.txt     # Dependências do projeto<br>
├── README.md            # Documentação<br>
```
-----------------------------------------------------------------------------------
<br>
Funcionalidades Futuras<br>

Integração com Docker para facilitar a implantação.<br>
Suporte a autenticação com biometria.<br>
Logs criptografados para maior **privacidade**.<br>
Contribuições
Sinta-se à vontade para abrir issues, propor melhorias ou fazer pull requests.
```
Faça um fork do repositório.
Crie uma nova branch: 

git checkout -b feature/nova-funcionalidade.

Envie as mudanças: 

git push origin feature/nova-funcionalidade.

Abra um pull request.<br>

Licença
Este projeto está sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.
```

Contato
Para dúvidas ou sugestões, entre em contato:

Autor: Gabriel Rozendo.
Email: roxy.py@protonmail.com