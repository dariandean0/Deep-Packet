#!/bin/bash
set -e

# Start all stage services in the background
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf &
sleep 3

clear
cat << 'BANNER'

  ██████╗ ███████╗███████╗██████╗     ██████╗  █████╗  ██████╗██╗  ██╗███████╗████████╗
  ██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝
  ██║  ██║█████╗  █████╗  ██████╔╝    ██████╔╝███████║██║     █████╔╝ █████╗     ██║
  ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝     ██╔═══╝ ██╔══██║██║     ██╔═██╗ ██╔══╝     ██║
  ██████╔╝███████╗███████╗██║         ██║     ██║  ██║╚██████╗██║  ██╗███████╗   ██║
  ╚═════╝ ╚══════╝╚══════╝╚═╝         ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝

BANNER

cat << 'INFO'
  ════════════════════════════════════════════════════════════════════════════════════════
  INCIDENT REPORT — CLASSIFIED
  ════════════════════════════════════════════════════════════════════════════════════════

  At 03:47 UTC an intrusion was detected on the internal network. The attacker moved
  laterally across multiple services before exfiltrating data through an unconventional
  channel. Our sensors captured traffic during the breach window.

  Your mission: trace the attacker's path through the network, recover the exfiltrated
  data, and retrieve the final flag.

  ════════════════════════════════════════════════════════════════════════════════════════
  STAGES
  ════════════════════════════════════════════════════════════════════════════════════════

    Stage 1  -->  http://localhost:8001      Network Analysis Portal (pcap)
    Stage 2  -->  UNKNOWN                   Unlocked by Stage 1
    Stage 3  -->  UNKNOWN                   Unlocked by Stage 2
    Stage 4  -->  UNKNOWN                   Unlocked by Stage 3

  ════════════════════════════════════════════════════════════════════════════════════════
  START HERE
  ════════════════════════════════════════════════════════════════════════════════════════

    You are inside the challenge container. Use curl to download files so they
    land here in the container where you can work on them directly.

    curl http://localhost:8001                        View the portal
    curl -O http://localhost:8001/capture.pcap        Download the capture
    tshark -r capture.pcap                            Begin your analysis

  ════════════════════════════════════════════════════════════════════════════════════════

INFO

exec bash
