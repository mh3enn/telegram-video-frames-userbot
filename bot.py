from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

if not SESSION_STRING:
    raise RuntimeError("SESSION_STRING is missing!")

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)


@client.on(events.NewMessage(pattern=r'^/ping$'))
async def ping_handler(event):
    await event.reply("pong ✅")


async def main():
    await client.connect()
    print("✅ Userbot is running")
    await client.run_until_disconnected()


asyncio.run(main())
