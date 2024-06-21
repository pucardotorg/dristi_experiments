# Use an NVIDIA CUDA base image with Python 3
FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

ENV PYTHON_VERSION=3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Avoid interactive prompts from apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install any needed packages
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get -qq update \
    && apt-get -qq install \
                   ffmpeg \
                   libsndfile1 \
                   python3-pip \
                   python${PYTHON_VERSION} \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch and torchvision with CUDA support
RUN pip3 install torch==2.0.0+cu118 torchvision==0.15.0+cu118 torchaudio==2.0.0+cu118 -f https://download.pytorch.org/whl/cu118/torch_stable.html

# Copy the requirements.txt file
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Copy the startup script
COPY start.sh start.sh

# Make the startup script executable
RUN chmod +x start.sh

# Make ports 8765 and 5000 available to the world outside this container
EXPOSE 8765
EXPOSE 5000

# Define environment variable
ENV NAME VoiceStreamAI

# Set the entrypoint to the startup script
ENTRYPOINT ["./start.sh"]
