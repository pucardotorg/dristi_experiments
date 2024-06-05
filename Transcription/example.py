import gradio as gr
from transformers import pipeline
import numpy as np
import os

transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

def transcribe(stream, new_chunk):
    sr, y = new_chunk
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))

    if stream is not None:
        stream = np.concatenate([stream, y])
    else:
        stream = y
    return stream, transcriber({"sampling_rate": sr, "raw": stream})["text"]


demo = gr.Interface(
    transcribe,
    ["state", gr.Audio(sources=["microphone"], streaming=True)],
    ["state", "text"],
    live=True,
)

os.environ['GRADIO_ANALYTICS_ENABLED'] = "False"

demo.launch()


# https://colab.research.google.com/github/sanchit-gandhi/notebooks/blob/main/fine_tune_whisper.ipynb
# https://github.com/pucardotorg/dristi_experiments
# https://github.com/ChakshuGautam/pg-rbac
# https://github.com/speechbrain/speechbrain