import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.node_id = str(uuid4()).replace('-', '')
        self.create_block(previous_hash='1', proof=100)  # Genesis block

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  # Сложность = 4 нуля


# ====================== FLASK ======================
app = Flask(__name__)
CORS(app)
blockchain = Blockchain()


@app.route('/')
def index():
    return render_template('node.html')


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    return jsonify({'message': f'Transaction will be added to Block {index}'}), 201


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Награда за майнинг
    blockchain.new_transaction(
        sender="0",
        recipient=blockchain.node_id,
        amount=1,
    )

    previous_hash = hashlib.sha256(json.dumps(last_block, sort_keys=True).encode()).hexdigest()
    block = blockchain.create_block(proof, previous_hash)

    return jsonify({
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    return jsonify({
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)