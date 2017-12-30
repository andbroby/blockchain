import hashlib
import json
import requests

from time import time
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain(object):
    """A chain"""
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.add_block(previous_hash=1, proof=100)

    def register_node(self, address):
        """
        Registers a new node to the decentralized network.
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def chain_is_valid(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            current_block = chain[current_index]
            if current_block['previous_hash'] != self.hash(last_block):
                return False

            last_block = current_block
            current_index += 1

        return True

    def resolve_chain_conflicts(self):
        """
        Runs through every node in the network to ensure consensus. The longest chain is taken to be authoritative.
        """
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if max_length < length and self.chain_is_valid(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def add_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        self.chain.append(block)

        return block

    def add_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.current_transactions.append(transaction)

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_str = json.dumps(block, sort_keys=True).encode()
        hashed_block = hashlib.sha256(block_str).hexdigest()

        return hashed_block

    def proof_of_work(self, last_proof):
        """
        Proof of Work used for mining. Obviously not the most efficient.
        """
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        A proof is valid if the last 4 digits of the hashed concatenated string of last proof and current proof are 0s
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hashed = hashlib.sha256(guess).hexdigest()

        return guess_hashed[:4] == '0000'