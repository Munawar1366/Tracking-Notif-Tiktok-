import requests
import time
import json
import os

TELEGRAM_BOT_TOKEN = "9160132670:AAEVfrzYHq_-OAPTtbhEgMgBXh3oMTkBRZY"
TELEGRAM_CHAT_ID = "7376896906"
TARGET_TIKTOK_USERNAME = "chica.holic"
CHECK_INTERVAL = 300

STATE_FILE = f"tiktok_{TARGET_TIKTOK_USERNAME}_state.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error kirim pesan Telegram: {e}")

def load_previous_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {"following": [], "followers": []}
    return None

def save_current_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def fetch_tiktok_data(username):
    url = f"https://www.tiktok.com/node/share/user/@{username}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"Error fetch data TikTok: {e}")
    return None

def check_tiktok_updates():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Memeriksa pembaruan untuk @{TARGET_TIKTOK_USERNAME}...")
    old_state = load_previous_state()
    raw_data = fetch_tiktok_data(TARGET_TIKTOK_USERNAME)

    if not raw_data or "userInfo" not in raw_data:
        print("Gagal mengambil data target TikTok.")
        return

    current_following = raw_data.get("followingList", []) 
    current_followers = raw_data.get("followerList", [])

    if old_state is None:
        save_current_state({
            "following": current_following,
            "followers": current_followers
        })
        print("State awal berhasil disimpan. Bot siap memantau perubahan!")
        send_telegram_msg(f"✅ **BOT TRACKER TIKTOK AKTIF!**\nMemantau target: `@{TARGET_TIKTOK_USERNAME}`")
        return

    old_following = set(old_state.get("following", []))
    old_followers = set(old_state.get("followers", []))

    new_following = set(current_following) - old_following
    new_followers = set(current_followers) - old_followers

    for user in new_following:
        msg = (f"🚨 **TARGET FOLLOW AKUN BARU!**\n\n"
               f"👤 Target: `@{TARGET_TIKTOK_USERNAME}`\n"
               f"➕ Baru mem-follow: `@{user}`\n"
               f"🔗 Link: https://www.tiktok.com/@{user}")
        send_telegram_msg(msg)

    for user in new_followers:
        msg = (f"🚨 **FOLLOWER BARU TARGET!**\n\n"
               f"👤 Target: `@{TARGET_TIKTOK_USERNAME}`\n"
               f"👥 Di-follow oleh: `@{user}`\n"
               f"🔗 Link: https://www.tiktok.com/@{user}")
        send_telegram_msg(msg)

    save_current_state({
        "following": list(current_following),
        "followers": list(current_followers)
    })

print(f"Bot Pemantau TikTok untuk @{TARGET_TIKTOK_USERNAME} Mulai Berjalan...")
while True:
    check_tiktok_updates()
    time.sleep(CHECK_INTERVAL)
