FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    git curl ca-certificates vim \
    python3 python3-pip python3-venv python3-dev \
    build-essential pkg-config \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install -U pip setuptools wheel \
    && python3 -m pip install -U cmake ninja setuptools_scm

# ---- 호스트 UID/GID로 유저 생성 ----
ARG USERNAME=dev
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} ${USERNAME} \
 && useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME}

WORKDIR /workspace
USER ${USERNAME}
CMD ["/bin/bash"]

