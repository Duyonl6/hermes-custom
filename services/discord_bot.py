import discord
from discord.ext import commands
import requests
import os

# ── Config ──────────────────────────────────────
# Load from bridge.env
def load_env():
    env_path = os.path.expanduser("~/.hermes/bridge.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    else:
        print(f"⚠️ bridge.env not found at {env_path}")

load_env()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "YOUR_TOKEN_HERE")
if DISCORD_TOKEN == "YOUR_TOKEN_HERE":
    print("⚠️ DISCORD_TOKEN is not set! Bot will not start.")
    exit(1)

HERMES_API_URL = "http://localhost:8000/chat"
SAVE_CACHE_URL = "http://localhost:8000/save_cache"

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Lưu mapping: bot_message_id → original_message_id
# Để khi user react vào bot message biết cache nào cần lưu
pending_reactions = {}

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')

@bot.event
async def on_message(message):
    print(f"[DEBUG] Received message: {message.content} from {message.author}")
    if message.author == bot.user:
        return

    # Chỉ reply khi được mention hoặc DM
    if not (bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel)):
        print(f"[DEBUG] Ignored message (no mention/not DM): {message.content[:50]}")
        return

    query = message.content.replace(f'<@{bot.user.id}>', '').strip()
    print(f'[DEBUG] Query after strip: \"{query}\"')
    if not query:
        return

    # Gửi "đang xử lý..."
    async with message.channel.typing():
        try:
            payload = {
                "message": query,
                "user": str(message.author),
                "message_id": str(message.id)
            }
            resp     = requests.post(HERMES_API_URL, json=payload, timeout=90)
            data     = resp.json()
            reply    = data.get("reply", "Không có phản hồi")
            source   = data.get("source", "llm")
            ask_save = data.get("ask_save", False)
            msg_id   = data.get("message_id", "")

            # Thêm badge nguồn
            if source == "cache":
                reply = f"⚡ **[Cache]**\n{reply}"
            else:
                reply = f"🤖 **[AI]**\n{reply}"

            # Gửi reply (Discord giới hạn 2000 ký tự)
            if len(reply) > 2000:
                for i in range(0, len(reply), 2000):
                    bot_msg = await message.channel.send(reply[i:i+2000])
            else:
                bot_msg = await message.channel.send(reply)

            # Nếu từ LLM → hỏi có muốn lưu cache không
            if ask_save and source == "llm" and msg_id:
                save_msg = await message.channel.send(
                    f"💾 Lưu câu trả lời này vào cache không?\n"
                    f"React ✅ để lưu | ❌ để bỏ qua"
                )
                await save_msg.add_reaction("✅")
                await save_msg.add_reaction("❌")

                # Lưu mapping để xử lý reaction
                pending_reactions[str(save_msg.id)] = msg_id

        except Exception as e:
            await message.channel.send(f"❌ Lỗi: {e}")

    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    msg_id = str(reaction.message.id)
    if msg_id not in pending_reactions:
        return

    original_msg_id = pending_reactions.pop(msg_id)

    if str(reaction.emoji) == "✅":
        # Gọi API lưu cache
        try:
            resp = requests.post(
                SAVE_CACHE_URL,
                json={"message_id": original_msg_id},
                timeout=10
            )
            data = resp.json()
            if data.get("status") == "saved":
                await reaction.message.edit(content="✅ **Đã lưu vào cache!**")
            else:
                await reaction.message.edit(content="⚠️ Không tìm thấy để lưu.")
        except Exception as e:
            await reaction.message.edit(content=f"❌ Lỗi lưu cache: {e}")

    elif str(reaction.emoji) == "❌":
        await reaction.message.edit(content="❌ **Bỏ qua, không lưu cache.**")

    # Xóa reaction buttons
    try:
        await reaction.message.clear_reactions()
    except:
        pass


@bot.command(name="cache")
async def cache_status(ctx):
    """Xem thống kê cache — dùng: !cache"""
    try:
        resp  = requests.get("http://localhost:8000/cache_stats", timeout=5)
        stats = resp.json()
        if stats.get("available"):
            await ctx.send(
                f"📊 **Cache Stats**\n"
                f"• Entries: `{stats['entries']}`\n"
                f"• TTL: `{stats['ttl']}s`\n"
                f"• Status: ✅ Online"
            )
        else:
            await ctx.send("⚠️ Cache không khả dụng")
    except Exception as e:
        await ctx.send(f"❌ Lỗi: {e}")


if __name__ == '__main__':
    print("🚀 Discord bot starting...")
    bot.run(DISCORD_TOKEN)
