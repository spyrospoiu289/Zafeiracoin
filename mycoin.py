# --- Blockchain logic ---
import hashlib
import json
from time import time
from flask import Flask, jsonify, request

class BlockChain:
    def __init__(self):
        self.chain = []
        self.pending_tx = []
        self.create_block(proof=1, prev_hash='0')

    def create_block(self, proof, prev_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'previous_hash': prev_hash,
            'transactions': self.pending_tx
        }
        self.pending_tx = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, receiver, amount):
        self.pending_tx.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        return self.last_block()['index'] + 1

    def last_block(self):
        return self.chain[-1]

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        return hashlib.sha256(guess).hexdigest()[:4] == "0000"

# --- Flask API setup ---
app = Flask(__name__)
blockchain = BlockChain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block()
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.add_transaction(sender="0", receiver="you", amount=1)

    block = blockchain.create_block(proof, blockchain.hash(last_block))
    return jsonify(block), 200

@app.route('/transactions', methods=['POST'])
def add_transaction():
    tx = request.get_json()
    index = blockchain.add_transaction(tx['sender'], tx['receiver'], tx['amount'])
    return jsonify({'message': f'Transaction will be added to block {index}'}), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    return jsonify({'chain': blockchain.chain, 'length': len(blockchain.chain)}), 200

if __name__ == '__main__':
    app.run(port=5000)
