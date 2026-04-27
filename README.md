# Deep-Packet
 
> *At 03:47 UTC an intrusion was detected on the internal network. The attacker moved laterally across multiple services before exfiltrating data through an unconventional channel. Trace the path. Recover the data. Retrieve the flag.*
 
A self-contained, four-stage Capture the Flag (CTF) challenge delivered as a single Docker container. Each stage is a distinct security discipline. Completing one reveals the entry point of the next.
 
---
 
## Stages
 
| # | Domain | Technique | Port |
|---|--------|-----------|------|
| 1 | Network Forensics | PCAP analysis / Base64 decoding | `8001` |
| 2 | Steganography | LSB pixel encoding / Vigenère cipher | `8002` |
| 3 | Web Security | SQL injection (auth bypass) | `8003` |
| 4 | Binary Exploitation | Stack buffer overflow / ret2win | `9004` |
 
---
 
## Quick Start
 
### Prerequisites
 
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)
- Python 3 with `scapy`, `Pillow`, and `numpy` (for artifact generation only)
### 1. Configure secrets
 
```bash
cp .env.example .env
# Edit .env and set your values:
#   VIGENERE_KEY, STAGE2_HOST, STAGE2_PORT, PLAINTEXT_SECRET, FLAG
```
 
### 2. Generate artifacts
 
```bash
cd generation_scripts
pip install scapy Pillow numpy
bash gen_all.sh
```
 
This produces:
- `stages/stage1/files/capture.pcap`
- `stages/stage2/files/signal.png`
### 3. Build and run
 
```bash
docker compose up --build
```
 
The challenge is now live. Connect a shell into the container to begin:
 
```bash
docker exec -it deep_packet bash
```
 
---
 
## Playing the Challenge
 
You start inside the container. The banner at login describes the scenario and lists your entry point.
 
```
curl http://localhost:8001          # View the Stage 1 portal
curl -O http://localhost:8001/capture.pcap
tshark -r capture.pcap              # Begin analysis
```
 
Each stage is intentionally undisclosed until the previous one is solved.
 
### Tools you will need
 
- **Stage 1** - `tshark`, `wireshark`, or any PCAP reader; `base64`
- **Stage 2** - `zsteg`, `exiftool`, a Vigenère decoder
- **Stage 3** - `curl`, a browser, or Burp Suite
- **Stage 4** - `pwntools`, `gdb` / `pwndbg`, `file`, `nm` / `objdump`
---
 
## Project Structure
 
```
Deep-Packet/
├── docker-compose.yml
├── Dockerfile
├── supervisord.conf
├── entrypoint.sh
├── bashrc                        # Login banner shown to players
├── .env                          # Secrets
├── generation_scripts/
│   ├── gen_all.sh                # Master generation script
│   ├── gen_pcap.py               # Stage 1: builds capture.pcap via Scapy
│   └── gen_img.py                # Stage 2: builds signal.png with LSB steg
└── stages/
    ├── stage1/
    │   ├── server.py             # HTTP server - serves capture.pcap on :8001
    │   └── files/                # capture.pcap (generated, gitignored)
    ├── stage2/
    │   ├── server.py             # HTTP server - serves signal.png on :8002
    │   └── files/                # signal.png (generated, gitignored)
    ├── stage3/
    │   └── server.py             # SQLi-vulnerable login portal on :8003
    └── stage4/
        ├── vuln.c                # Vulnerable C source (gets() overflow)
        └── files/                # flag.txt
```
 
---
 
## How Each Stage Works
 
### Stage 1 - Network Forensics
 
`gen_pcap.py` uses Scapy to synthesise a realistic TCP stream. An HTTP POST body carries a Base64-encoded payload; decoding it reveals the Stage 2 address. Red-herring DNS and TLS packets are included to reward careful filtering.
 
### Stage 2 - Steganography + Cryptography
 
`gen_img.py` generates a spectrogram-style PNG and embeds a secret message in the **least-significant bit** of the red channel. The message is a Vigenère-encrypted URL pointing to Stage 3. The cipher key is stored in the image's `Artist` PNG metadata field.
 
### Stage 3 - SQL Injection
 
A minimal Python HTTP server presents a login form backed by SQLite. User input is concatenated directly into the query — no parameterisation. A well-placed comment sequence bypasses authentication and reveals the Stage 4 service address and binary download.
 
### Stage 4 - Binary Exploitation
 
A 32-bit ELF compiled with all mitigations disabled (`-fno-stack-protector -no-pie -z execstack`). The `vuln()` function reads unbounded input via `gets()` into a 64-byte buffer. Overwriting the saved return address with the address of `win()` causes the binary to open and print `flag.txt`.
 
---
 
## Generating a Fresh Challenge
 
All secrets are driven by `.env`. To regenerate with new values:
 
```bash
# 1. Update .env
# 2. Re-run generation
bash generation_scripts/gen_all.sh
# 3. Rebuild the container
docker compose up --build
```
 
---
 
## Port Reference
 
| Port | Service |
|------|---------|
| `8001` | Stage 1 — Network Analysis Portal |
| `8002` | Stage 2 — Signal Intelligence |
| `8003` | Stage 3 — Internal Diagnostic Console |
| `9004` | Stage 4 — Binary service (via `socat`) |
 
---
 
## License
 
MIT — see [LICENSE](LICENSE).
