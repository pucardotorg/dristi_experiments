import os
from threading import Thread
from queue import Queue
import asyncio

from dotenv import load_dotenv
import discord
from discord.ext import commands
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

CHANNELS = {
    "transcription": None,
    "ocr": None,
    "validation": None
}

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Issue(BaseModel):
    category: str
    text: str

message_queue = Queue()

@bot.event
async def on_ready():
    for channel_name in CHANNELS:
        CHANNELS[channel_name] = discord.utils.get(bot.get_all_channels(), name=channel_name)
    bot.loop.create_task(process_messages())

async def process_messages():
    while True:
        if not message_queue.empty():
            category, text = message_queue.get()
            channel = CHANNELS.get(category)
            if channel:
                await channel.send(f"New {category} issue: {text}")
        await asyncio.sleep(1)  # Wait for a second before checking again

@app.post("/submit-issue")
async def submit_issue(issue: Issue):
    if issue.category not in CHANNELS:
        raise HTTPException(status_code=400, detail="Invalid category")
    message_queue.put((issue.category, issue.text))
    return {"message": f"{issue.category.capitalize()} issue queued successfully!"}

def run_bot():
    bot.run(os.getenv('TOKEN'))

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8002)

if __name__ == "__main__":
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    try:
        run_api()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
        bot_thread.join()