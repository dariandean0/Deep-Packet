FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Base + server infrastructure
RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip \
        gcc \
        gcc-multilib \
        libc6-i386 \
        lib32gcc-s1 \
        socat \
        supervisor \
        curl \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Stage 1 — PCAP analysis
RUN apt-get update && apt-get install -y \
        tshark \
        tcpdump \
        binutils \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --no-cache-dir scapy

# Stage 2 — Steganography
RUN apt-get update && apt-get install -y \
        libimage-exiftool-perl \
        ruby \
    && rm -rf /var/lib/apt/lists/* \
    && gem install zsteg --no-document \
    && pip3 install --no-cache-dir Pillow

# Stage 3 — SQL injection (sqlite3 is part of the Python stdlib, no extra deps)

# Stage server files live under /opt/ctf — not visible in the player's workdir
COPY stages/stage1/server.py /opt/ctf/stages/stage1/server.py
COPY stages/stage2/server.py /opt/ctf/stages/stage2/server.py
COPY stages/stage3/server.py /opt/ctf/stages/stage3/server.py

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY entrypoint.sh /entrypoint.sh

WORKDIR /work

# Stage 1: /srv/stage1  — bind-mounted at runtime (capture.pcap)
# Stage 2: /srv/stage2  — bind-mounted at runtime (signal.png)
# Stage 4: /srv/vuln    — compiled above; also served by stage4_files on 8004
EXPOSE 8001 8002 8003 9004 8004

CMD ["/entrypoint.sh"]
