"""
gen_pcap.py Generate Stage 1 capture.pcap

Builds a realistic TCP stream containing an HTTP POST whose body carries
a Base64-encoded payload. When decoded, the payload reveals Stage 2's
address: NEXT_STAGE=<STAGE2_HOST>:<STAGE2_PORT>

Requires: scapy
    pip install scapy
"""

import base64
import os
import sys
from pathlib import Path

try:
    from scapy.all import (
        Ether, IP, TCP, Raw, wrpcap, Packet
    )
except ImportError:
    sys.exit("ERROR: scapy not installed. Run: pip install scapy")

# Configuration from environment (set by generate_all.sh sourcing .env)
STAGE2_HOST = os.environ.get("STAGE2_HOST", "stage2")
STAGE2_PORT = os.environ.get("STAGE2_PORT", "8002")
OUT_PATH = Path(__file__).parent.parent / "stages" / "stage1" / "files" / "capture.pcap"

# Build the encoded payload
secret = f"NEXT_STAGE = {STAGE2_HOST}:{STAGE2_PORT}"
encoded = base64.b64encode(secret.encode()).decode()

# Craft a realistic HTTP POST body
http_body = f"data = {encoded}"
http_request = (
    f"POST /api/upload HTTP/1.1\r\n"
    f"Host: 10.0.0.1\r\n"
    f"User-Agent: Mozilla/5.0 (compatible; InternalAgent/1.0)\r\n"
    f"Content-Type: application/x-www-form-urlencoded\r\n"
    f"Content-Length: {len(http_body)}\r\n"
    f"Connection: close\r\n"
    f"\r\n"
    f"{http_body}"
)

http_response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/plain\r\n"
    "Content-Length: 2\r\n"
    "\r\n"
    "OK"
)

# Static addresses for a convincing but fake TCP stream
CLIENT_IP = "10.0.0.5"
SERVER_IP = "10.0.0.1"
CLIENT_PORT = 54321
SERVER_PORT = 80

# Base Ethernet + IP templates
def pkt(src_ip, dst_ip, sport, dport, flags, seq, ack, payload = b""):
    return (
        Ether(src = "aa:bb:cc:dd:ee:01", dst = "aa:bb:cc:dd:ee:02") /
        IP(src = src_ip, dst = dst_ip, ttl = 64) /
        TCP(sport = sport, dport = dport, flags = flags, seq = seq, ack = ack,
            window = 65535) /
        (Raw(load = payload) if payload else b"")
    )

# Assemble the packet list: SYN --> SYN-ACK --> ACK --> PSH/ACK (request)
#   --> ACK --> PSH/ACK (response) --> FIN-ACK --> FIN-ACK --> ACK
req_bytes = http_request.encode()
res_bytes = http_response.encode()

packets = [
    # 3-way handshake
    pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "S",  seq = 1000, ack = 0),
    pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "SA", seq = 5000, ack = 1001),
    pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "A",  seq = 1001, ack = 5001),
    # HTTP POST (client --> server)
    pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "PA", seq = 1001, ack = 5001, payload = req_bytes),
    # Server ACKs the request
    pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "A",  seq = 5001, ack = 1001 + len(req_bytes)),
    # HTTP 200 response (server --> client)
    pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "PA", seq = 5001, ack = 1001 + len(req_bytes), payload = res_bytes),
    # Client ACKs response
    pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "A",  seq = 1001 + len(req_bytes), ack = 5001 + len(res_bytes)),
    # Teardown
    pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "FA", seq = 1001 + len(req_bytes), ack = 5001 + len(res_bytes)),
    pkt(SERVER_IP, CLIENT_IP, SERVER_PORT, CLIENT_PORT, "FA", seq = 5001 + len(res_bytes), ack = 1002 + len(req_bytes)),
    pkt(CLIENT_IP, SERVER_IP, CLIENT_PORT, SERVER_PORT, "A",  seq = 1002 + len(req_bytes), ack = 5002 + len(res_bytes)),
]

# Also include some red-herring traffic before the interesting stream
noise = [
    pkt("10.0.0.3", "10.0.0.1", 44444, 53, "PA", seq = 100, ack = 0,
        payload = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"),  # fake DNS
    pkt("10.0.0.1", "10.0.0.3", 53, 44444, "PA", seq = 200, ack = 101,
        payload = b"\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00"),
    pkt("10.0.0.4", "10.0.0.1", 33333, 443, "S", seq = 9000, ack = 0),
    pkt("10.0.0.1", "10.0.0.4", 443, 33333, "R", seq = 0, ack = 9001),
]

all_packets = noise + packets

# Write
OUT_PATH.parent.mkdir(parents = True, exist_ok = True)
wrpcap(str(OUT_PATH), all_packets)
print(f"[+] capture.pcap written to {OUT_PATH}")
print(f"[+] Encoded payload: {encoded}")
print(f"[+] Decoded reveals: {secret}")