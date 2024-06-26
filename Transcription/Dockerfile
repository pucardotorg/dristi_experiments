# Use an NVIDIA CUDA base image with Python 3
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

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
                   libsqlite3-dev \
                   python${PYTHON_VERSION} \
    && rm -rf /var/lib/apt/lists/*

# Update alternatives to set the default python3 version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 && \
    update-alternatives --set python3 /usr/bin/python${PYTHON_VERSION}

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Copy the requirements.txt file
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Make port 8765 available to the world outside this container
EXPOSE 8765

# Define environment variable
ENV NAME VoiceStreamAI

# Set the entrypoint to your application
ENTRYPOINT ["python3", "-m", "src.main"]

# Provide a default command (can be overridden at runtime)
CMD ["--host", "0.0.0.0", "--port", "8765"]