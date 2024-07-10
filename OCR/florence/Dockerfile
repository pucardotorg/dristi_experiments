# Use the official PyTorch image as a base image
FROM pytorch/pytorch:latest

# Set the working directory in the container
WORKDIR /app

# Install dependencies for the application
RUN apt-get update && \
    apt-get install -y \
    poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .


# Expose port 8000 to the outside
EXPOSE 8000

# Set the default command to run the application
CMD ["hypercorn", "--bind", "0.0.0.0:8000", "api:app"]