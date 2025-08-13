#!/usr/bin/env bash
set -euo pipefail

# Initialize
private_key=""
rpc_url=""
chain_id=""

usage() {
  echo "Usage: $0 --private_key <hexkey> --rpc_url <url> --chain_id <id>"
  exit 1
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --private_key) private_key="${2:-}"; shift 2 ;;
    --rpc_url)     rpc_url="${2:-}";     shift 2 ;;
    --chain_id)    chain_id="${2:-}";    shift 2 ;;
    -h|--help)     usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

# Validate
if [[ -z "$private_key" || -z "$rpc_url" || -z "$chain_id" ]]; then
  echo "Error: all arguments are mandatory."
  usage
fi

echo "🚀 Deploying Federation contract"
echo "Private Key: [HIDDEN]"
echo "RPC URL    : $rpc_url"
echo "Chain ID   : $chain_id"

# Run in Docker
docker run -it --rm \
  --network host \
  -v "$(pwd)/smart-contracts":/smart-contracts \
  -u "$(id -u):$(id -g)" \
  -e PRIVATE_KEY="$private_key" \
  -e RPC_URL="$rpc_url" \
  -e CHAIN_ID="$chain_id" \
  hardhat:latest \
  bash -lc "npx hardhat run scripts/deploy_federation.js --network quickstart"
