"""Telegram GIF search: the same results as the GIF panel in a Telegram chat (inline bot @gif).

Needs the user's own Telegram login, kept OUTSIDE the repo in ~/.claude/telegram-gif/ (or the folder in
$REACTFORGE_TG_DIR):
  .env             TG_API_ID=...  TG_API_HASH=...   (from my.telegram.org -> API development tools)
  session.session  created by `python -m reactforge.tgmeme login` (full access to the account: never share)
`pip install telethon`. Anything missing -> search() returns None and memes.py falls back to yt-dlp/Imgflip.
"""
from __future__ import annotations
import asyncio, os
from pathlib import Path


MAX_UPSCALE = 1.4          # a meme is never shown bigger than this x its own pixels (blur standard)
PART_BOX = (1113, 713)     # the "part" box in a 1920x1080 frame (render.py: 58% x 66%)


def sharp_enough(w: int, h: int, box: tuple[int, int] = PART_BOX) -> bool:
    return w > 0 and h > 0 and min(box[0] / w, box[1] / h) <= MAX_UPSCALE


def _dir() -> Path:
    return Path(os.environ.get("REACTFORGE_TG_DIR") or Path.home() / ".claude" / "telegram-gif")


def _creds() -> tuple[int, str] | None:
    f = _dir() / ".env"
    if not f.exists():
        return None
    env = dict(l.split("=", 1) for l in f.read_text(encoding="utf-8").splitlines() if "=" in l)
    try:
        return int(env["TG_API_ID"].strip()), env["TG_API_HASH"].strip()
    except (KeyError, ValueError):
        return None


async def _search(q: str, dest: Path, max_secs: float) -> Path | None:
    from telethon import TelegramClient
    api_id, api_hash = _creds()
    client = TelegramClient(str(_dir() / "session"), api_id, api_hash)
    await client.connect()
    try:
        if not await client.is_user_authorized():
            print("   ⚠ telegram: chưa đăng nhập (chạy: python -m reactforge.tgmeme login)")
            return None
        for r in await client.inline_query("gif", q):
            doc = getattr(r, "document", None)
            if doc is None:
                continue
            va = next((a for a in doc.attributes if hasattr(a, "duration")), None)
            dur, w, h = (va.duration, getattr(va, "w", 0), getattr(va, "h", 0)) if va else (0, 0, 0)
            if dur and dur > max_secs:
                continue
            if not sharp_enough(w, h):   # too small: would look blurry, try the next result
                continue
            got = await r.download_media(file=str(dest))
            return Path(got) if got else None
    finally:
        await client.disconnect()
    return None


def search(q: str, dest: Path, max_secs: float = 8.0) -> tuple[Path, str] | None:
    """First short GIF Telegram offers for `q`, saved next to `dest` (extension decided by Telegram)."""
    try:
        import telethon  # noqa: F401
    except ImportError:
        return None
    if _creds() is None or not (_dir() / "session.session").exists():
        return None
    got = asyncio.run(_search(q, dest, max_secs))
    return (got, f"telegram-gif:{q}") if got else None


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["login"]:
        from telethon import TelegramClient
        creds = _creds()
        if creds is None:
            sys.exit(f"Thiếu {_dir() / '.env'} (TG_API_ID, TG_API_HASH)")
        _dir().mkdir(parents=True, exist_ok=True)
        with TelegramClient(str(_dir() / "session"), *creds) as c:   # asks phone + OTP on first run
            print("Logged in as", c.loop.run_until_complete(c.get_me()).first_name)
    elif sys.argv[1:2] == ["search"]:
        out = search(sys.argv[2], Path(sys.argv[3]) if len(sys.argv) > 3 else Path("tg-test"))
        print(out)
    else:
        print("usage: python -m reactforge.tgmeme login | search <query> [dest]")
