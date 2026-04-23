import uuid
from flask import Flask, request, jsonify
import requests
import asyncio
import threading
import json
import os
import sys

# ── Semantic Cache ──────────────────────────────
sys.path.insert(0, '/home/ducdu/.hermes/plugins')
try:
    from semantic_cache import cache_get, cache_set, cache_stats, _embedder
    CACHE_AVAILABLE = True
    print("✅ Semantic cache loaded")
except Exception as e:
    CACHE_AVAILABLE = False
    print(f"⚠️ Cache không load được: {e}")

app = Flask(__name__)

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

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    print("⚠️ OPENROUTER_API_KEY is empty! API calls will fail.")
    
MODEL = "deepseek/deepseek-chat-v3-0324"

# Lưu các message đang chờ user xác nhận lưu cache
# key = discord_message_id, value = {query, response}
pending_cache = {}

# ── Gọi OpenRouter ──────────────────────────────
def call_openrouter(message: str) -> str:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": message}]
        },
        timeout=60
    )
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return f"Lỗi API: {result.get('error', {}).get('message', str(result))}"

# ── Route /chat ──────────────────────────────────
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get("message", "")
    user  = data.get("user", "Unknown")
    msg_id = data.get("message_id", "") or str(uuid.uuid4())

    # Bước 1: Check cache
    if CACHE_AVAILABLE:
        loop = asyncio.new_event_loop()
        cached = loop.run_until_complete(cache_get(query))
        loop.close()
        if cached:
            return jsonify({
                "reply": cached,
                "source": "cache",
                "ask_save": False
            })

    # Bước 2: Cache MISS → gọi OpenRouter
    reply = call_openrouter(query)

    # Bước 3: Lưu vào pending, hỏi user có muốn cache không
    if CACHE_AVAILABLE and msg_id:
        pending_cache[msg_id] = {"query": query, "response": reply}

    return jsonify({
        "reply": reply,
        "source": "llm",
        "ask_save": CACHE_AVAILABLE,
        "message_id": msg_id
    })

# ── Route /save_cache ────────────────────────────
@app.route('/save_cache', methods=['POST'])
def save_cache():
    data   = request.json
    msg_id = data.get("message_id", "") or str(uuid.uuid4())

    if msg_id in pending_cache:
        entry = pending_cache.pop(msg_id)
        loop  = asyncio.new_event_loop()
        loop.run_until_complete(cache_set(entry["query"], entry["response"]))
        loop.close()
        return jsonify({"status": "saved"})

    return jsonify({"status": "not_found"})

# ── Route /cache_stats ───────────────────────────
@app.route('/cache_stats', methods=['GET'])
def get_cache_stats():
    if not CACHE_AVAILABLE:
        return jsonify({"available": False})
    loop  = asyncio.new_event_loop()
    stats = loop.run_until_complete(cache_stats())
    loop.close()
    return jsonify(stats)


if __name__ == '__main__':
    # Warm up cache model khi start (load 1 lần duy nhất)
    if CACHE_AVAILABLE:
        print("🔥 Warming up embedding model...")
        try:
            _embedder.encode("warmup", normalize_embeddings=True)
            print("✅ Model ready")
        except Exception as e:
            print(f"⚠️ Warmup failed: {e}")

    print("🚀 Hermes API server starting on port 8000...")
    app.run(host='127.0.0.1', port=8000, debug=False)
