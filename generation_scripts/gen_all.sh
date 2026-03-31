#!/usr/bin/env bash
# generate_all.sh — Master generation script
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SCRIPT_DIR}/.."
ENV_FILE="${ROOT}/.env"

# Load environment variables
if [[ ! -f "${ENV_FILE}" ]]; then
    echo "ERROR: .env file not found at ${ENV_FILE}"
    echo "       Copy .env.example to .env and fill in your values."
    exit 1
fi

set -a
# shellcheck source=/dev/null
source "${ENV_FILE}"
set +a

echo "================================================================"
echo "  DEEP PACKET — CTF Challenge Generation"
echo "================================================================"
echo ""

# Check Python dependencies
echo "[*] Checking Python dependencies..."
python3 -c "import scapy"   2>/dev/null || { echo "ERROR: scapy missing — pip install scapy"; exit 1; }
python3 -c "import PIL"     2>/dev/null || { echo "ERROR: Pillow missing — pip install Pillow"; exit 1; }
python3 -c "import numpy"   2>/dev/null || { echo "ERROR: numpy missing — pip install numpy"; exit 1; }
echo "[+] Python dependencies OK"

# Stage 1: Generate capture.pcap
echo ""
echo "[Stage 1] Generating capture.pcap..."
python3 "${SCRIPT_DIR}/gen_pcap.py"


# Summary
echo ""
echo "================================================================"
echo "  Generation complete. Artifact summary:"
echo "================================================================"
echo ""
ls -lh "${ROOT}/stages/stage1/files/" 2>/dev/null || true
echo ""
echo "  Next step: docker compose up --build"
echo ""