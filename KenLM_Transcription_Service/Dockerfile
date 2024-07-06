# Use an official Python runtime as a parent image
FROM python:3.9-slim

WORKDIR /app

# Install system packages required for building kenlm
RUN apt-get update && apt-get install -y cmake g++ zlib1g-dev

# Install requirements
COPY requirements.txt requirements.txt
RUN pip3 install  --no-cache-dir --prefer-binary -r requirements.txt

# Install kenlm using pip
RUN pip3 install https://github.com/kpu/kenlm/archive/master.zip
RUN apt-get update && apt-get install -y wget

RUN apt-get install -y build-essential cmake libboost-system-dev libboost-thread-dev libboost-program-options-dev libboost-test-dev libeigen3-dev zlib1g-dev libbz2-dev liblzma-dev

# Download the files using wget
RUN wget "https://drive.google.com/uc?export=download&id=1frSw5-qfRMgrYs4QL961s2yYuq2KplEM" -O '5gram_model.bin'
RUN wget "https://drive.google.com/uc?export=download&id=1o31Z4TZbAOEt6E8Rx7VMONJOGJH-5Mwk" -O 'lexicon.txt'
RUN wget "https://drive.google.com/uc?export=download&id=1eVWwarCm8Wqq3vYqsE9f2jvrp-rvr6QZ" -O 'texts.txt'

RUN wget "https://drive.google.com/uc?export=download&id=1SkTN4Q36VT0XYBT639D_eMcmsRqWWVab" -O '5gram_model_eng.bin' 
RUN wget "https://drive.google.com/uc?export=download&id=1XopfrZ3g1uSIawWZKa3EpFTU23Mp1U8S" -O 'lexicon_eng.txt'
RUN wget "https://drive.google.com/uc?export=download&id=1VkAShoA10ESU_n8pX7o9gFh8xJMvhiqO" -O 'texts_eng.txt'

# Dowload the kenlm training files
RUN wget -O - https://kheafield.com/code/kenlm.tar.gz | tar xz
RUN mkdir kenlm/build && cd kenlm/build && cmake .. && make -j2

# Copy the rest of the application code to the working directory
COPY . /app/

EXPOSE 8000

# Set the entrypoint for the container
CMD ["hypercorn", "--bind", "0.0.0.0:8000", "api:app"]
