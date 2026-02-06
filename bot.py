from telethon import TelegramClient, events
import os
from dotenv import load_dotenv

# متغیرهای مخفی رو از .env بخون
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# ساخت کلاینت تلگرام
client = TelegramClient("userbot", API_ID, API_HASH)


@client.on(events.NewMessage(pattern=r'^/ping$'))
async def ping_handler(event):
    await event.reply("pong ✅")


print("Userbot is starting...")
client.start()
client.run_until_disconnected()
