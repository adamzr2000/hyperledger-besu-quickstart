# Hyperledger Besu Quickstart

**Author:** Adam Zahir Rodríguez

This project provides a ready-to-use local [Hyperledger Besu](https://besu.hyperledger.org/) blockchain environment using the **Quorum Developer Quickstart** tool. It includes Docker-based builds, a pre-configured monitoring stack, and utilities for deploying smart contracts.

---

## Build Docker images
From the repository root:
```bash
docker compose build
```
This will build all images defined in [docker-compose.yml](./docker-compose.yml) using the Dockerfiles under [dockerfiles](./dockerfiles)

---

## Launch Quorum Developer Quickstart
```bash
./start_quorum_dev_quickstart.sh
```
Follow the prompts to configure:
- Ethereum client: **Hyperledger Besu**
- Private transactions: **No**
- Logging: **Loki**
- Monitoring: **Blockscout (Yes)**  
- Config directory: e.g., `./quorum-test-network`

---

## View available endpoints
```bash
./list.sh
```
Example services exposed:
- JSON-RPC HTTP: `http://localhost:8545`  
- JSON-RPC WS: `ws://localhost:8546`  
- Block Explorer: `http://localhost:25000/explorer/nodes`  
- Blockscout: `http://localhost:26000/`  
- Prometheus: `http://localhost:9090/graph`  
- Grafana: `http://localhost:3000/`

---

## Deploy Federation Smart Contract
```bash
./deploy_smart_contract.sh \
  --chain_id 1337 \
  --rpc_url http://localhost:8545 \
  --private_key 0x8bbbb1b345af56b560a5b20bd4b0ed1cd8cc9958a16262bc75118453cb546df7
```

---

## Manage the network
- **Start**:
  ```bash
  ./run.sh
  ```
- **Stop**:
  ```bash
  ./stop.sh
  ```
- **Remove** (delete containers and volumes):
  ```bash
  ./remove.sh
  ```

---

## Credentials and Keys
When the network is created, **all node credentials, keys, and account data** are stored inside the generated configuration folder (default: `quorum-test-network/config/`).

Key locations:
- **Node keys & addresses**:  
  `quorum-test-network/config/nodes/<node_name>/`
  - `accountKeystore` – Encrypted account key (JSON format)
  - `accountPrivateKey` – Raw private key (⚠ not encrypted)
  - `accountPassword` – Password to unlock the keystore
  - `nodekey` / `nodekey.pub` – Node identity keys
  - `tm.key` / `tm.pub` – Tessera transaction manager keys
- **EthSigner key**:  
  `quorum-test-network/config/ethsigner/`

⚠ **Security note:** These keys are for **development only**. Do not reuse them in production environments.
