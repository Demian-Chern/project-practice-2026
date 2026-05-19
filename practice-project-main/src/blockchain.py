import binascii
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests

MINING_DIFFICULTY = 4  # Количество нулей в начале хеша (сложность)
MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 1


class Blockchain:
    def __init__(self):
        self.transactions = []
        self.chain = []
        self.nodes = set()
        # Генерация уникального ID для узла майнера
        self.node_id = str(uuid4()).replace('-', '')
        # Создание генезис-блока
        self.create_block(0, '00')

    def register_node(self, node_url):
        """Добавление нового узла в сеть"""
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def verify_transaction_signature(self, sender_address, signature, transaction):
        """Проверка соответствия подписи публичному ключу отправителя"""
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        try:
            return verifier.verify(h, binascii.unhexlify(signature))
        except (ValueError, TypeError):
            return False

    def submit_transaction(self, sender_address, recipient_address, value, signature):
        """Добавление транзакции в пул после верификации подписи"""
        transaction = {
            'sender_address': sender_address,
            'recipient_address': recipient_address,
            'value': value
        }

        # Системная награда за майнинг идет без подписи
        if sender_address == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1

        # Проверка подписи для обычных транзакций
        if self.verify_transaction_signature(sender_address, signature, transaction):
            self.transactions.append(transaction)
            return len(self.chain) + 1
        return False

    def create_block(self, nonce, previous_hash):
        """Создание нового блока и добавление его в цепочку"""
        block = {
            'block_number': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }
        self.transactions = []
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        """SHA-256 хеширование блока"""
        block_string = json.dumps(block, sort_keys=True).encode()
        import hashlib
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self):
        """Алгоритм Доказательства выполнения работы (PoW)"""
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)
        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1
        return nonce

    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """Проверка удовлетворения хеша условию сложности (ведущие нули)"""
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode('utf8')
        import hashlib
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty

    def valid_chain(self, chain):
        """Проверка целостности и валидности переданной цепочки блокчейна"""
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            # Проверка соответствия предыдущего хеша
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Проверка корректности PoW: исключаем транзакцию-награду (последнюю)
            transactions = block['transactions'][:-1] if block['transactions'] else []
            if not self.valid_proof(transactions, block['previous_hash'], block['nonce']):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """Консенсус: замена локальной цепи самой длинной валидной цепью в сети"""
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.exceptions.RequestException:
                continue

        if new_chain:
            self.chain = new_chain
            return True
        return False


app = Flask(__name__)
CORS(app)
blockchain = Blockchain()


@app.route('/')
def index():
    return render_template('node.html')


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    required = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400

    transaction_result = blockchain.submit_transaction(
        values['sender_address'], values['recipient_address'], values['amount'], values['signature']
    )
    if transaction_result == False:
        return jsonify({'message': 'Invalid Transaction!'}), 406
    else:
        return jsonify({'message': f'Transaction will be added to Block {transaction_result}'}), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.chain[-1]
    nonce = blockchain.proof_of_work()

    # Выдача награды за нахождение блока
    blockchain.submit_transaction(
        sender_address=MINING_SENDER,
        recipient_address=blockchain.node_id,
        value=MINING_REWARD,
        signature=""
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(nonce, previous_hash)

    response = {
        'message': "New Block Forged",
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('nodes').replace(" ", "").split(',')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    return jsonify({'message': 'New nodes have been added', 'total_nodes': list(blockchain.nodes)}), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        return jsonify({'message': 'Our chain was replaced', 'new_chain': blockchain.chain}), 200
    return jsonify({'message': 'Our chain is authoritative', 'chain': blockchain.chain}), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    app.run(host='127.0.0.1', port=args.port, debug=True)