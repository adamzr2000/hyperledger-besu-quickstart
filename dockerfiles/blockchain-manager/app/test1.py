import os
import logging
from web3 import Web3
import time
from blockchain_interface import BlockchainInterface, FederationEvents

eth_address      = os.getenv("ETH_ADDRESS")
eth_private_key  = os.getenv("ETH_PRIVATE_KEY")
eth_node_url     = os.getenv("ETH_NODE_URL")
contract_addr_raw= os.getenv("CONTRACT_ADDRESS")

# -- guard against missing configurations --
required = {
    "ETH_ADDRESS":      eth_address,
    "ETH_PRIVATE_KEY":  eth_private_key,
    "ETH_NODE_URL":     eth_node_url,
    "CONTRACT_ADDRESS": contract_addr_raw,
}
missing = [k for k,v in required.items() if not v]
if missing:
    raise RuntimeError(f"ERROR: missing environment variables: {', '.join(missing)}")

# -- validate & normalize the contract address --
try:
    contract_address = Web3.to_checksum_address(contract_addr_raw)
except Exception:
    raise RuntimeError(f"ERROR: CONTRACT_ADDRESS '{contract_addr_raw}' is not a valid Ethereum address")

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize blockchain interface
blockchain = BlockchainInterface(
    eth_address=eth_address,
    private_key=eth_private_key,
    eth_node_url=eth_node_url,
    abi_path="/smart-contracts/artifacts/contracts/Federation.sol/Federation.json",
    contract_address=contract_address
)

tx_hash = blockchain.register_domain("example.org")
print("tx:", tx_hash)

# wait for mining and fetch receipt
time.sleep(10)

rcpt = blockchain.get_transaction_receipt(tx_hash)
print(rcpt)

info = blockchain.get_operator_info()
print("operator info:", info)