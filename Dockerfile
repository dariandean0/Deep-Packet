FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install all dependencies for every stage in one layer
RUN apt-get update && apt-get install -y \
        python3 \
        gcc \
        gcc-multilib \
        libc6-i386 \
        lib32gcc-s1 \
        socat \
        supervisor \
        tshark \
        curl \
        wget \
        binutils \
    && rm -rf /var/lib/apt/lists/*

# Stage server files live under /opt/ctf — not visible in the player's workdir
COPY stages/stage1/server.py /opt/ctf/stages/stage1/server.py
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY entrypoint.sh /entrypoint.sh

WORKDIR /work

# Stage 1: /srv/stage1  — bind-mounted at runtime (capture.pcap)
# Stage 2: /srv/stage2  — bind-mounted at runtime (signal.png)
# Stage 4: /srv/vuln    — compiled above; also served by stage4_files on 8004
EXPOSE 8001 8002 9004 8004

CMD ["/entrypoint.sh"]
