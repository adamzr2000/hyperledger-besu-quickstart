# blockchain_interface.py — web3.py v7.13.0

import json
import logging
import threading
from enum import Enum

from web3 import Web3
from web3.providers.legacy_websocket import LegacyWebSocketProvider
from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class FederationEvents(str, Enum):
    OPERATOR_REGISTERED = "OperatorRegistered"
    OPERATOR_REMOVED = "OperatorRemoved"
    SERVICE_ANNOUNCEMENT = "ServiceAnnouncement"
    NEW_BID = "NewBid"
    SERVICE_ANNOUNCEMENT_CLOSED = "ServiceAnnouncementClosed"
    CONSUMER_ENDPOINT_UPDATED = "ConsumerEndpointUpdated"
    PROVIDER_ENDPOINT_UPDATED = "ProviderEndpointUpdated"
    SERVICE_DEPLOYED = "ServiceDeployed"
    SERVICE_CANCELLED = "ServiceCancelled"


class BlockchainInterface:
    def __init__(self, eth_address, private_key, eth_node_url, abi_path, contract_address):
        # --- Provider (v7) ---
        if eth_node_url.startswith(("ws://", "wss://")):
            self.web3 = Web3(LegacyWebSocketProvider(eth_node_url))
        elif eth_node_url.startswith(("http://", "https://")):
            self.web3 = Web3(Web3.HTTPProvider(eth_node_url))
        else:
            raise ValueError("eth_node_url must start with ws://, wss://, http:// or https://")

        # PoA/QBFT header fix
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if not self.web3.is_connected():
            raise ConnectionError(f"Cannot connect to Ethereum node at {eth_node_url}")

        # --- Keys & Address ---
        self.private_key = private_key
        acct = self.web3.eth.account.from_key(self.private_key)
        derived_addr = acct.address  # checksum

        if eth_address:
            provided = Web3.to_checksum_address(eth_address)
            if provided != derived_addr:
                logger.warning(
                    "Provided ETH_ADDRESS (%s) != address from private key (%s). Using derived.",
                    provided, derived_addr
                )
            self.eth_address = derived_addr
        else:
            self.eth_address = derived_addr

        # --- ABI & Contract ---
        with open(abi_path, "r") as f:
            abi = json.load(f).get("abi")
        if not abi:
            raise ValueError("ABI not found in JSON")

        self.contract = self.web3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=abi
        )

        logger.info(f"Web3 initialized. Address: {self.eth_address}")
        logger.info(f"Connected to Ethereum node {eth_node_url} | Version: {self.web3.client_version}")

        self.chain_id = self.web3.eth.chain_id

        # Nonce from pending to avoid collisions
        self._nonce_lock = threading.Lock()
        self._local_nonce = self.web3.eth.get_transaction_count(self.eth_address, block_identifier='pending')

    def send_signed_transaction(self, build_transaction: dict) -> str:
        with self._nonce_lock:
            build_transaction['nonce'] = self._local_nonce
            self._local_nonce += 1

        build_transaction.setdefault('chainId', self.chain_id)

        # Force legacy tx with explicit gasPrice (often 0 on devnets)
        build_transaction['type'] = 0                      # ← legacy
        build_transaction['gasPrice'] = build_transaction.get('gasPrice', 0)

        # (Optional) set a gas limit if your node won’t estimate it for you)
        # if 'gas' not in build_transaction:
        #     build_transaction['gas'] = self.contract.functions.addOperator("x").estimate_gas({'from': self.eth_address})

        signed = self.web3.eth.account.sign_transaction(build_transaction, self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        return tx_hash.hex()

    def get_transaction_receipt(self, tx_hash: str) -> dict:
        receipt = self.web3.eth.get_transaction_receipt(tx_hash)
        if not receipt:
            raise Exception("Transaction receipt not found")

        rd = dict(receipt)
        for k in ('blockHash', 'transactionHash', 'logsBloom'):
            if k in rd and hasattr(rd[k], 'hex'):
                rd[k] = rd[k].hex()

        rd['from_address'] = rd.pop('from')
        rd['to_address'] = rd.pop('to')

        logs = []
        for log in rd.get('logs', []):
            d = dict(log)
            for hk in ('blockHash', 'transactionHash'):
                if hk in d and hasattr(d[hk], 'hex'):
                    d[hk] = d[hk].hex()
            d['topics'] = [t.hex() if hasattr(t, 'hex') else t for t in d.get('topics', [])]
            logs.append(d)
        rd['logs'] = logs

        block = self.web3.eth.get_block(receipt['blockNumber'])
        rd['timestamp'] = block['timestamp']
        return rd

    def create_event_filter(self, event_name: FederationEvents, last_n_blocks: int = None):
        block_number = self.web3.eth.block_number
        from_block = max(0, block_number - last_n_blocks) if last_n_blocks else block_number
        event_abi = getattr(self.contract.events, event_name.value)
        return event_abi.create_filter(from_block=from_block)

    def register_domain(self, domain_name: str) -> str:
        tx = self.contract.functions.addOperator(domain_name).build_transaction({
            'from': self.eth_address,
            'chainId': self.chain_id,
        })
        return self.send_signed_transaction(tx)

    def unregister_domain(self) -> str:
        tx = self.contract.functions.removeOperator().build_transaction({
            'from': self.eth_address,
            'chainId': self.chain_id,
        })
        return self.send_signed_transaction(tx)

    def get_operator_info(self):
        return self.contract.functions.getOperatorInfo(self.eth_address).call()
