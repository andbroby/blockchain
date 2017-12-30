
import hashlib
import json

from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask
from flask import jsonify
from flask import request

from blockchain import Blockchain

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.add_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.add_block(proof, previous_hash)

    response = {
        'message': "Succesfully mined new block",
        "index": block["index"],
        "timestamp": block["timestamp"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']

    if not all(required_key in values for required_key in required):
        return "Invalid request - missing values", 400

    index_of_transaction = blockchain.add_transaction(values['sender'], values['recipient'], values['amount'])
    response = f"Transaction added to block at {index_of_transaction}"
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    chain = blockchain.chain

    response = {
        'chain': chain,
        'length': len(chain)
    }

    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')

    if not nodes:
        return "Invalid request. Supply a list of nodes.", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added.',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    chain_replaced = blockchain.resolve_chain_conflicts()

    if chain_replaced:
        response = {
            'message': 'Chain was replaced.',
            'chain': blockchain.chain,
        }
    else:
        response = {
            'message': 'No changes needed. Current chain is authoritative.',
            'chain': blockchain.chain,
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)