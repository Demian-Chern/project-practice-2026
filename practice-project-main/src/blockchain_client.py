import binascii
from collections import OrderedDict
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


class Transaction:
    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value

    def to_dict(self):
        """Возвращает информацию о транзакции в виде упорядоченного словаря без приватного ключа"""
        return OrderedDict({
            'sender_address': self.sender_address,
            'recipient_address': self.recipient_address,
            'value': self.value
        })

    def sign_transaction(self):
        """Подпись транзакции с использованием приватного ключа RSA"""
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


@app.route('/')
def index():
    return render_template('client.html')


@app.route('/wallet/new', methods=['GET'])
def new_wallet():
    """Генерация пары ключей RSA (публичный и приватный)"""
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()

    response = {
        'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
        'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
    }
    return jsonify(response), 200


@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
    """Формирование и подписание транзакции на основе переданных данных"""
    sender_address = request.form['sender_address']
    sender_private_key = request.form['sender_private_key']
    recipient_address = request.form['recipient_address']
    value = request.form['amount']

    transaction = Transaction(sender_address, sender_private_key, recipient_address, value)

    response = {
        'transaction': transaction.to_dict(),
        'signature': transaction.sign_transaction()
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='Port to listen on')
    args = parser.parse_args()
    app.run(host='127.0.0.1', port=args.port, debug=True)