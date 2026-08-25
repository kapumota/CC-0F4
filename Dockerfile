# CC-0F4 - entorno reproducible 2026-2
#
# Una sola imagen CUDA-capable:
# - sin --gpus all: el código puede ejecutarse en CPU;
# - con --gpus all y runtime NVIDIA configurado: PyTorch usa GPU.
#
# Tag fijado para evitar cambios durante el semestre.
FROM pytorch/pytorch:2.11.0-cuda12.8-cudnn9-runtime

ARG USERNAME=cc0f4
ARG USER_UID=1000
ARG USER_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    JUPYTER_ENABLE_LAB=yes

WORKDIR /workspace/CC-0F4

# La imagen base ya contiene PyTorch 2.11.0 + CUDA runtime.
COPY requirements.txt /tmp/requirements.txt

RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/requirements.txt \
    && groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} \
       --create-home --shell /bin/bash ${USERNAME} \
    && mkdir -p /workspace/CC-0F4 \
    && chown -R ${USERNAME}:${USERNAME} /workspace/CC-0F4

USER ${USERNAME}
ENV HOME=/home/${USERNAME}

EXPOSE 8888

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--ServerApp.root_dir=/workspace/CC-0F4"]
