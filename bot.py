from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterVideo
import os
import re
import cv2
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
OWNER_ID = int(os.getenv("OWNER_ID"))

if not SESSION_STRING:
    raise RuntimeError("SESSION_STRING is missing!")

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)
async def download_with_progress(event, video_message, frames):
    # پیام اولیه
    status_msg = await event.reply(f"⏳ در حال دانلود ویدیو برای {frames} فریم... 0%")

    def progress(current, total):
        percent = int(current * 100 / total)
        # هر 10٪ یک بار آپدیت کنیم
        if percent % 10 == 0:
            # edit کردن پیام تلگرام
            try:
                client.loop.create_task(
                    status_msg.edit(f"⏳ در حال دانلود ویدیو برای {frames} فریم... {percent}%")
                )
            except:
                pass

    path = await client.download_media(video_message, progress_callback=progress)
    await status_msg.edit(f"✅ دانلود کامل شد!\nمسیر: `{path}`")
    return path
async def extract_and_send_frames(event, video_path, frames_count):
    # پوشه فریم‌ها
    os.makedirs("frames", exist_ok=True)

    # باز کردن ویدیو
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        await event.reply("❌ ویدیو خالی یا نامعتبر است!")
        return

    # فاصله بین فریم‌ها
    step = max(1, total_frames // frames_count)
    
    frame_paths = []
    for i in range(0, total_frames, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame_file = f"frames/frame_{i}.jpg"
        cv2.imwrite(frame_file, frame)
        frame_paths.append(frame_file)
        # می‌تونی اینجا پیام کوتاه برای پیشرفت ارسال کنی اگر خواستی
    
    cap.release()

    # ارسال فریم‌ها (مثلا فقط 5 فریم اول برای نمونه)
    for fp in frame_paths[:5]:
        await event.reply(file=fp)

    await event.reply(f"✅ استخراج فریم‌ها کامل شد!\nتعداد استخراج شده: {len(frame_paths)}")
@client.on(events.NewMessage(pattern=r'^/frames\s+(\d+)$'))
async def frames_handler(event):
    # فقط خودت
    if event.sender_id != OWNER_ID:
        return

    # باید ریپلای باشه
    if not event.is_reply:
        await event.reply("❌ روی ویدیو ریپلای کن")
        return

    reply = await event.get_reply_message()

    # باید ویدیو باشه
    if not reply.video:
        await event.reply("❌ پیام ریپلای شده ویدیو نیست")
        return

    # تعداد فریم
    frames_count = int(event.pattern_match.group(1))

    if frames_count < 1 or frames_count > 50:
        await event.reply("❌ تعداد فریم باید بین 1 تا 50 باشه")
        return

    # ساخت پوشه
    os.makedirs("downloads", exist_ok=True)

    # دانلود ویدیو با نمایش درصد
    video_path = await download_with_progress(event, reply, frames_count)
    # استخراج و ارسال فریم‌ها
    await extract_and_send_frames(event, video_path, frames_count)
@client.on(events.NewMessage(pattern=r'^/ping$'))
async def ping_handler(event):
    await event.reply("pong ✅")


async def main():
    await client.connect()
    print("✅ Userbot is running")
    await client.run_until_disconnected()


asyncio.run(main())
