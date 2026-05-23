import os

bot = os.getenv("BOT_TOKEN")
chat = os.getenv("CHAT_ID")

print("=== DEBUG START ===")

if bot:
    print("BOT exists: YES")
    print("BOT first chars:", bot[:8])
else:
    print("BOT exists: NO")

if chat:
    print("CHAT:", chat)
else:
    print("CHAT: MISSING")

print("=== DEBUG END ===")
