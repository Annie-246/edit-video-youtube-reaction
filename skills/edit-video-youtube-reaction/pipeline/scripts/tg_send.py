#!/usr/bin/env python3
"""Send a text or a video to anh via Telegram (bot token from ~/video_bot/.env, chat id anh).
Usage: tg_send.py "message"            | tg_send.py --video file.mp4 "caption"
"""
import os, sys, json, urllib.request, urllib.parse, mimetypes, uuid
from pathlib import Path

def env(k):
    for line in (Path.home()/"video_bot/.env").read_text().splitlines():
        if line.startswith(k + "="): return line.split("=",1)[1].strip().strip('"').strip("'")
    return None

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or env("TELEGRAM_BOT_TOKEN")
CHAT = os.environ.get("TG_CHAT_ID") or env("TG_CHAT_ID")
if not CHAT:
    sys.exit("Chưa có TG_CHAT_ID — đặt trong ~/video_bot/.env hoặc biến môi trường.\nLấy id bằng cách nhắn cho bot rồi mở https://api.telegram.org/bot<TOKEN>/getUpdates")
API = f"https://api.telegram.org/bot{TOKEN}"

def post_multipart(url, fields, files):
    boundary = uuid.uuid4().hex; body = b""
    for k, v in fields.items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    for k, p in files.items():
        p = Path(p); ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{p.name}\"\r\nContent-Type: {ctype}\r\n\r\n".encode() + p.read_bytes() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.load(urllib.request.urlopen(req, timeout=600))

def main():
    a = sys.argv[1:]
    if a and a[0] == "--video":
        r = post_multipart(API + "/sendVideo", {"chat_id": CHAT, "caption": a[2] if len(a) > 2 else "", "supports_streaming": "true"}, {"video": a[1]})
    elif a and a[0] == "--file":
        r = post_multipart(API + "/sendDocument", {"chat_id": CHAT, "caption": a[2] if len(a) > 2 else ""}, {"document": a[1]})
    else:
        data = urllib.parse.urlencode({"chat_id": CHAT, "text": " ".join(a)}).encode()
        r = json.load(urllib.request.urlopen(API + "/sendMessage", data=data, timeout=60))
    print("ok" if r.get("ok") else r)

if __name__ == "__main__":
    main()
