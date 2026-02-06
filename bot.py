from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION_STRING")

client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)


@client.on(events.NewMessage(pattern=r'^/ping$'))
async def ping_handler(event):
    await event.reply("pong ✅")


print("Userbot is starting with StringSession...")
client.start()
client.run_until_disconnected()
