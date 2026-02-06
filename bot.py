from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterVideo
from telethon.errors.rpcerrorlist import MessageNotModifiedError
import os
import cv2
import asyncio
import random

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
    status_msg = await event.reply(f"⏳ در حال دانلود ویدیو برای {frames} فریم... 0%")
    last_percent = -1  # برای ذخیره آخرین درصد

    def progress(current, total):
        nonlocal last_percent
        percent = int(current * 100 / total)

        if percent != last_percent:
            last_percent = percent
            async def safe_edit():
                try:
                    await status_msg.edit(f"⏳ در حال دانلود ویدیو برای {frames} فریم... {percent}%")
                except MessageNotModifiedError:
                    pass
            asyncio.create_task(safe_edit())

    path = await client.download_media(video_message, progress_callback=progress)
    await status_msg.edit(f"✅ دانلود کامل شد!\nمسیر: `{path}`")
    return path

async def extract_and_send_frames(event, video_path, frames_count):
    os.makedirs("frames", exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        await event.reply("❌ ویدیو خالی یا نامعتبر است!")
        return

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
    
    cap.release()

    # انتخاب ۱۰ فریم به صورت رندوم
    num_to_send = min(10, len(frame_paths))
    selected_frames = random.sample(frame_paths, num_to_send)

    caption_text = f"✅ استخراج فریم‌ها کامل شد!\nتعداد استخراج شده: {len(frame_paths)}"

    # ارسال به صورت مدیا گروپ واقعی
    await client.send_file(
        entity=event.chat_id,
        file=selected_frames,
        caption=caption_text,
        reply_to=event.reply_to_msg_id,
        force_document=False
    )

    # حذف فایل‌ها و ویدیو
    try:
        for fp in frame_paths:
            os.remove(fp)
        os.remove(video_path)
        await event.reply(f"🗑 فایل‌ها با موفقیت پاک شدند!", reply_to=event.reply_to_msg_id)
    except Exception as e:
        await event.reply(f"⚠ خطا در پاک کردن فایل‌ها: {e}", reply_to=event.reply_to_msg_id)

@client.on(events.NewMessage(pattern=r'^/frames\s+(\d+)$'))
async def frames_handler(event):
    if event.sender_id != OWNER_ID:
        return
    if not event.is_reply:
        await event.reply("❌ روی ویدیو ریپلای کن")
        return

    reply = await event.get_reply_message()
    if not reply.video:
        await event.reply("❌ پیام ریپلای شده ویدیو نیست")
        return

    frames_count = int(event.pattern_match.group(1))
    if frames_count < 1 or frames_count > 50:
        await event.reply("❌ تعداد فریم باید بین 1 تا 50 باشه")
        return

    os.makedirs("downloads", exist_ok=True)

    video_path = await download_with_progress(event, reply, frames_count)
    await extract_and_send_frames(event, video_path, frames_count)

@client.on(events.NewMessage(pattern=r'^/ping$'))
async def ping_handler(event):
    await event.reply("pong ✅")

async def main():
    await client.connect()
    print("✅ Userbot is running")
    await client.run_until_disconnected()

asyncio.run(main())
