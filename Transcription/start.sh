#!/bin/bash

# Check if the VAD_ARGS environment variable is set
if [ -z "$VAD_ARGS" ]; then
  echo "VAD_ARGS is not set. Exiting."
  exit 1
fi

# Start the main application with the provided VAD_ARGS
python3 -m src.main --host 0.0.0.0 --port 8765 --vad-args "$VAD_ARGS" &

# Start the post serve script
python3 src/post_serve.py

# Wait for all background processes to finish
wait
