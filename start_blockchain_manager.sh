#!/usr/bin/env bash

container_name="blockchain-manager"
eth_address="0xf0e2db6c8dc6c681bb5d6ad121a107f300e9b2b5"
eth_private_key="8bbbb1b345af56b560a5b20bd4b0ed1cd8cc9958a16262bc75118453cb546df7"
eth_node_url="http://localhost:8545"
contract_address="0x00fFD3548725459255f1e78A61A07f1539Db0271"


# Run the container
docker run \
  --rm -it \
  --name "$container_name" \
  --net host \
  --env ETH_ADDRESS="$eth_address" \
  --env ETH_PRIVATE_KEY="$eth_private_key" \
  --env ETH_NODE_URL="$eth_node_url" \
  --env CONTRACT_ADDRESS="$contract_address" \
  -v "$(pwd)/smart-contracts":/smart-contracts \
  -v "$(pwd)/experiments":/experiments \
  -v "$(pwd)/dockerfiles/blockchain-manager/app":/app \
  blockchain-manager-test:latest \
  bash
