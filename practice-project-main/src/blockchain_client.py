import binascii
import json
from collections import OrderedDict
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


class Transaction:
    def __init__(self, sender_address, sender_private_key, recipient_address, amount):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.amount = amount

    def to_dict(self):
        return OrderedDict({
            'sender': self.sender_address,
            'recipient': self.recipient_address,
            'amount': self.amount
        })

    def sign_transaction(self):
        """Подписываем транзакцию приватным ключом"""
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(json.dumps(self.to_dict(), sort_keys=True).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')


@app.route('/')
def index():
    return render_template('client.html')


@app.route('/wallet/new', methods=['GET'])
def new_wallet():
    """Генерация новой пары ключей"""
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()

    response = {
        'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
        'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def generate_transaction():
    """Создание и подписание транзакции"""
    values = request.form

    transaction = Transaction(
        values['sender_address'],
        values['sender_private_key'],
        values['recipient_address'],
        values['amount']
    )

    signature = transaction.sign_transaction()

    response = {
        'transaction': transaction.to_dict(),
        'signature': signature
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=True)