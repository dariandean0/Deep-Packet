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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY stages/stage1/server.py stages/stage1/server.py

# Stage 1: /srv/stage1  — bind-mounted at runtime (capture.pcap)
# Stage 2: /srv/stage2  — bind-mounted at runtime (signal.png)
# Stage 4: /srv/vuln    — compiled above; also served by stage4_files on 8004
EXPOSE 8001 8002 9004 8004

