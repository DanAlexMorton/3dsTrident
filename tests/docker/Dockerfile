FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DEVKITPRO=/opt/devkitpro
ENV DEVKITARM=$DEVKITPRO/devkitARM
ENV PATH=$DEVKITARM/bin:$DEVKITPRO/tools/bin:$PATH

# Build essentials + OpenGL (Mesa llvmpipe for software rendering) + xvfb
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git ca-certificates wget gnupg \
    python3 python3-pip \
    libgl-dev libgl1-mesa-dri libegl1-mesa libgles2-mesa-dev \
    libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev \
    libwayland-dev libxkbcommon-dev \
    mesa-utils xvfb \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# RetroArch from PPA
RUN add-apt-repository -y ppa:libretro/stable \
    && apt-get update \
    && apt-get install -y --no-install-recommends retroarch \
    && rm -rf /var/lib/apt/lists/*

# devkitPro for building 3DS test ROMs
RUN wget -q https://apt.devkitpro.org/install-devkitpro-pacman \
    && chmod +x ./install-devkitpro-pacman \
    && echo "Y" | ./install-devkitpro-pacman \
    && dkp-pacman -S --noconfirm 3ds-dev \
    && rm -f ./install-devkitpro-pacman

WORKDIR /workspace

ENTRYPOINT ["/bin/bash"]
