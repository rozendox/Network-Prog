import hashlib
import json
from time import time
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse
import requests

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Cria o bloco gênesis
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Adiciona um novo nó à lista de nós.
        :param address: Endereço do nó. Exemplo: 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Determina se uma blockchain é válida.
        :param chain: Uma blockchain.
        :return: True se válido, False caso contrário.
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Verifica se o hash do bloco é válido
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Verifica se a prova de trabalho é válida
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Este é o algoritmo de consenso, ele resolve conflitos
        substituindo nossa cadeia pela cadeia mais longa da rede.
        :return: True se nossa cadeia foi substituída, False caso contrário.
        """
        neighbours = self.nodes
        new_chain = None

        # Apenas queremos cadeias mais longas que a nossa
        max_length = len(self.chain)

        # Pega e verifica todas as cadeias da rede
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Verifica se o comprimento é maior e se a cadeia é válida
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Substitui nossa cadeia se descobrirmos uma nova, válida e mais longa
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        """
        Cria um novo bloco na blockchain.
        :param proof: A prova dada pelo algoritmo PoW.
        :param previous_hash: Hash do bloco anterior.
        :return: Novo bloco.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reseta a lista atual de transações
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Cria uma nova transação para ir para o próximo bloco.
        :param sender: Endereço do remetente.
        :param recipient: Endereço do destinatário.
        :param amount: Quantidade.
        :return: O índice do bloco que guardará a transação.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Cria um hash SHA-256 de um bloco.
        :param block: Bloco.
        """
        # Precisamos garantir que o dicionário esteja ordenado, ou teremos hashes inconsistentes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Retorna o último bloco da cadeia
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Algoritmo simples de prova de trabalho:
         - Encontre um número p' tal que hash(pp') contenha 4 zeros à esquerda, onde p é o proof anterior e p' é o novo proof
        :param last_proof: Proof anterior.
        :return: Novo proof.
        """
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valida a prova: hash(last_proof, proof) contém 4 zeros à esquerda?
        :param last_proof: Proof anterior.
        :param proof: Proof atual.
        :return: True se válido, False caso contrário.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Interface do Blockchain usando Flask

app = Flask(__name__)

# Gera um identificador único global para este nó
node_identifier = str(uuid4()).replace('-', '')

# Instancia a classe Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Executa o algoritmo PoW para obter a próxima proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Recebe uma recompensa por encontrar a proof.
    # O remetente "0" significa que este nó minerou uma nova moeda.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge o novo bloco adicionando-o à cadeia
    block = blockchain.new_block(proof)

    response = {
        'message': "Novo bloco forjado",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Verifique se os campos obrigatórios estão no POST
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Valores ausentes', 400

    # Cria uma nova transação
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transação será adicionada ao bloco {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Erro: Por favor, forneça uma lista de nós", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'Novos nós foram adicionados',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Nossa cadeia foi substituída',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Nossa cadeia é autoritária',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
